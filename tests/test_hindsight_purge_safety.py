"""Safety regressions for purge-stale.sql; only an ephemeral local PostgreSQL cluster is used."""
import os
import pathlib
import shutil
import socket
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SQL = ROOT / "deepcli/tools/hindsight-lifecycle/purge-stale.sql"


def postgres_bins():
    """Prefer PATH tools; otherwise select the highest installed versioned bin dir."""
    initdb = shutil.which("initdb")
    pg_ctl = shutil.which("pg_ctl")
    psql = shutil.which("psql")
    dirs = sorted(pathlib.Path("/usr/lib/postgresql").glob("*/bin"), reverse=True)
    if not initdb or not pg_ctl:
        for directory in dirs:
            if not initdb and (directory / "initdb").exists():
                initdb = str(directory / "initdb")
            if not pg_ctl and (directory / "pg_ctl").exists():
                pg_ctl = str(directory / "pg_ctl")
    # psql may be on PATH even if server binaries are not.
    if not psql:
        for directory in dirs:
            if (directory / "psql").exists():
                psql = str(directory / "psql")
                break
    return initdb, pg_ctl, psql


INITDB, PG_CTL, PSQL = postgres_bins()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(INITDB and PG_CTL and PSQL, "PostgreSQL initdb/pg_ctl/psql unavailable")
class PurgeSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.geteuid() == 0:
            raise unittest.SkipTest("initdb refuses root; run tests as an unprivileged local user")
        cls.tmp = tempfile.TemporaryDirectory(prefix="hindsight-purge-test-")
        cls.base = pathlib.Path(cls.tmp.name)
        cls.data, cls.sock = cls.base / "data", cls.base / "socket"
        cls.sock.mkdir()
        cls.port = free_port()
        cls.started = False
        try:
            subprocess.run([INITDB, "-D", str(cls.data), "-A", "trust", "--no-locale"], check=True, stdout=subprocess.DEVNULL)
            subprocess.run([PG_CTL, "-D", str(cls.data), "-o", f"-F -k {cls.sock} -p {cls.port} -h ''", "-w", "start"], check=True, stdout=subprocess.DEVNULL)
            cls.started = True
        except BaseException:
            if cls.started:
                subprocess.run([PG_CTL, "-D", str(cls.data), "-m", "immediate", "-w", "stop"], check=False, stdout=subprocess.DEVNULL)
            cls.tmp.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tmp"):
            if getattr(cls, "started", False):
                subprocess.run([PG_CTL, "-D", str(cls.data), "-m", "immediate", "-w", "stop"], check=False, stdout=subprocess.DEVNULL)
            cls.tmp.cleanup()

    def psql(self, sql=None, apply=False, succeeds=True):
        # A socket directory as -h forces Unix-domain transport; the server is
        # started with -h '' so it never listens on TCP.
        cmd = [PSQL, "-X", "-v", "ON_ERROR_STOP=1", "-h", str(self.sock), "-p", str(self.port), "-d", "postgres", "-At"]
        if apply:
            cmd += ["-v", "purge_apply=1"]
        if sql is not None:
            cmd += ["-c", sql]
        else:
            cmd += ["-f", str(SQL)]
        result = subprocess.run(cmd, text=True, capture_output=True)
        if succeeds and result.returncode != 0:
            self.fail(result.stdout + result.stderr)
        if not succeeds and result.returncode == 0:
            self.fail("expected psql failure, but command succeeded")
        return result

    def reset(self, extra=""):
        self.psql("DROP SCHEMA public CASCADE; CREATE SCHEMA public; "
                  "CREATE TABLE public.banks(bank_id text PRIMARY KEY); "
                  "INSERT INTO public.banks VALUES ('deepagent::termux-monorepo'), ('termux-monorepo::primary'); "
                  "CREATE TABLE public.memory_units(id integer PRIMARY KEY, bank_id text NOT NULL REFERENCES public.banks(bank_id)); "
                  "CREATE TABLE public.documents(id integer PRIMARY KEY, bank_id text NOT NULL REFERENCES public.banks(bank_id)); "
                  "INSERT INTO public.memory_units VALUES (1,'deepagent::termux-monorepo'); "
                  "INSERT INTO public.documents VALUES (1,'deepagent::termux-monorepo'); " + extra)

    def scalar(self, query):
        return self.psql(query).stdout.strip()

    def test_dry_run_is_unchanged(self):
        self.reset()
        self.psql()
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.banks WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_allowlisted_apply_and_unrelated_bank_id_untouched(self):
        self.reset("CREATE TABLE public.audit_log(id integer, bank_id text); INSERT INTO public.audit_log VALUES (1,'deepagent::termux-monorepo');")
        self.psql(apply=True)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='termux-monorepo::primary'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.documents WHERE bank_id='termux-monorepo::primary'"), "1")
        self.assertEqual(self.scalar("SELECT bank_id FROM public.audit_log"), "deepagent::termux-monorepo")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.banks WHERE bank_id='deepagent::termux-monorepo'"), "0")

    def test_unknown_fk_aborts_before_any_mutation(self):
        self.reset("CREATE TABLE public.unknown_dep(id integer, bank_id text REFERENCES public.banks(bank_id)); INSERT INTO public.unknown_dep VALUES(1,'deepagent::termux-monorepo');")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("unknown foreign-key dependency", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_unique_conflict_rolls_back_all_changes(self):
        self.reset("ALTER TABLE public.memory_units ADD CONSTRAINT memory_bank_unique UNIQUE(bank_id); INSERT INTO public.memory_units VALUES (2,'termux-monorepo::primary');")
        self.psql(apply=True, succeeds=False)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.documents WHERE bank_id='deepagent::termux-monorepo'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.banks WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_missing_target_aborts(self):
        self.reset("DELETE FROM public.banks WHERE bank_id='termux-monorepo::primary';")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("target bank", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_inherited_allowlisted_table_fails_before_mutation(self):
        self.reset("CREATE TABLE public.memory_child() INHERITS (public.memory_units);")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("standalone, non-partitioned", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.banks WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_partitioned_bank_fails_before_mutation(self):
        self.reset("ALTER TABLE public.banks RENAME TO old_banks; CREATE TABLE public.banks(bank_id text NOT NULL) PARTITION BY LIST(bank_id); CREATE TABLE public.banks_p PARTITION OF public.banks FOR VALUES IN ('deepagent::termux-monorepo'); INSERT INTO public.banks VALUES ('deepagent::termux-monorepo');")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("standalone, non-partitioned", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_missing_allowlisted_fk_fails_before_mutation(self):
        self.reset("ALTER TABLE public.memory_units DROP CONSTRAINT memory_units_bank_id_fkey;")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("lacks the verified bank_id FK", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def test_malformed_allowlisted_fk_fails_before_mutation(self):
        self.reset("ALTER TABLE public.memory_units DROP CONSTRAINT memory_units_bank_id_fkey; ALTER TABLE public.memory_units ADD COLUMN other_bank_id text; ALTER TABLE public.memory_units ADD CONSTRAINT wrong_bank_fk FOREIGN KEY(other_bank_id) REFERENCES public.banks(bank_id);")
        result = self.psql(apply=True, succeeds=False)
        self.assertIn("lacks the verified bank_id FK", result.stderr)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")

    def assert_no_side_effect(self):
        result = self.psql(apply=True, succeeds=False)
        self.assertEqual(self.scalar("SELECT count(*) FROM public.side_effects"), "0")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo'"), "1")
        self.assertEqual(self.scalar("SELECT count(*) FROM public.banks WHERE bank_id='deepagent::termux-monorepo'"), "1")
        return result

    def test_unexpected_trigger_aborts_before_side_effect(self):
        self.reset("CREATE TABLE public.side_effects(value text); "
                   "CREATE FUNCTION public.log_change() RETURNS trigger LANGUAGE plpgsql AS $$ "
                   "BEGIN INSERT INTO public.side_effects VALUES ('changed'); RETURN NEW; END $$; "
                   "CREATE TRIGGER log_update AFTER UPDATE ON public.memory_units "
                   "FOR EACH ROW EXECUTE FUNCTION public.log_change();")
        self.assertIn("triggers, or rules", self.assert_no_side_effect().stderr)

    def test_unexpected_rule_aborts_before_side_effect(self):
        self.reset("CREATE TABLE public.side_effects(value text); "
                   "CREATE RULE log_update AS ON UPDATE TO public.documents "
                   "DO ALSO INSERT INTO public.side_effects VALUES ('changed');")
        self.assertIn("triggers, or rules", self.assert_no_side_effect().stderr)

    def test_indirect_cascade_is_an_unknown_dependency(self):
        self.reset("ALTER TABLE public.memory_units ADD UNIQUE(bank_id); "
                   "CREATE TABLE public.side_effects(value text REFERENCES "
                   "public.memory_units(bank_id) ON UPDATE CASCADE);")
        self.assertIn("unknown foreign-key dependency", self.assert_no_side_effect().stderr)

    def test_row_security_is_unsupported(self):
        self.reset("CREATE TABLE public.side_effects(value text); "
                   "ALTER TABLE public.memory_units ENABLE ROW LEVEL SECURITY;")
        self.assertIn("row security", self.assert_no_side_effect().stderr)


if __name__ == "__main__":
    unittest.main()
