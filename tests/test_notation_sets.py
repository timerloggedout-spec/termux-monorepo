"""Notation-sets proposal tests — taxonomy, six frameworks, NSE-015 IR, docs refs."""
from pathlib import Path

CATEGORY_THEORY_NOTATION = {
    "morphism": {
        "symbol": "f: A → B",
        "domain_type": "source",
        "codomain_type": "target",
        "meaning": "f is an arrow from object A to object B",
    },
    "composition": {
        "symbol": "g ∘ f",
        "alt_symbol": "g f",
        "order": "right_to_left",
        "meaning": "composition g after f",
    },
    "diagrammatic_composition": {
        "symbol": "f ; g",
        "order": "left_to_right",
        "meaning": "composition f then g",
    },
    "monad_bind": {
        "symbol": "f >>= g",
        "class": "domain_specific_fp",
        "meaning": "Haskell/FP bind; not universal diagrammatic composition",
    },
    "hom_set": {
        "symbol": "Hom_C(A, B)",
        "alt_symbol": "C(A, B)",
        "meaning": "collection of all arrows from A to B",
    },
    "identity": {
        "symbol": "id_A",
        "alt_symbol": "1_A",
        "meaning": "mandatory identity arrow on object A",
    },
    "functor": {
        "symbol": "F: C → D",
        "meaning": "structure-preserving map between categories C and D",
    },
    "natural_transformation": {
        "symbol": "α: F ⇒ G",
        "meaning": "mapping between functors F and G",
    },
    "opposite_category": {
        "symbol": "C^op",
        "meaning": "category C with all arrows reversed",
    },
    "product": {
        "symbol": "A × B",
        "dual_of": "A ⊔ B",
        "meaning": "categorical product dual of coproduct",
    },
    "coproduct": {
        "symbol": "A ⊔ B",
        "alt_symbol": "A + B",
        "dual_of": "A × B",
        "meaning": "categorical sum / coproduct dual of product",
    },
    "exponential_object": {
        "symbol": "Y^X",
        "meaning": "internal object of arrows from X to Y",
    },
}

CROSS_DOMAIN_MAPPINGS = [
    {
        "framework": "Category Theory",
        "arrow": "f: A → B",
        "composition": "g ∘ f",
        "identity": "id_A",
    },
    {
        "framework": "Set Theory",
        "arrow": "f: X → Y",
        "composition": "(g ∘ f)(x) = g(f(x))",
        "identity": "I(x) = x",
    },
    {
        "framework": "Formal Logic",
        "arrow": "A ⇒ B",
        "composition": "(A ⇒ B) ∧ (B ⇒ C) ⇒ (A ⇒ C)",
        "identity": "A ⇒ A",
    },
    {
        "framework": "Type Theory & Functional Programming",
        "arrow": "f :: A -> B",
        "composition": "g . f",
        "identity": "id",
    },
    {
        "framework": "Order Theory (Posets)",
        "arrow": "x ≤ y",
        "composition": "x ≤ y ∧ y ≤ z ⇒ x ≤ z",
        "identity": "x ≤ x",
    },
    {
        "framework": "Lambda Lang (Λ)",
        "arrow": "atom / conceptual token",
        "composition": "atom sequencing / handoff",
        "identity": "stable atom id",
    },
]


def canonical_ir_encode(item_type: str, **params) -> str:
    """Encode category theory notation into Grimoire Canonical IR (NSE-015).

    Functor form is F:<src-cat>:<tgt-cat> (no label field).
    """
    if item_type == "object":
        return f"O:{params['id']}"
    if item_type == "morphism":
        return f"M:{params['src']}:{params['tgt']}:{params['label']}"
    if item_type == "composition":
        return f"COMP({params['m1']},{params['m2']})"
    if item_type == "identity":
        return f"ID({params['obj']})"
    if item_type == "functor":
        return f"F:{params['src_cat']}:{params['tgt_cat']}"
    if item_type == "natural_transformation":
        return f"NAT:{params['src_fun']}:{params['tgt_fun']}:{params['label']}"
    raise ValueError(f"Unknown item type: {item_type}")


def test_category_theory_notation_completeness():
    required_keys = {
        "morphism",
        "composition",
        "diagrammatic_composition",
        "monad_bind",
        "hom_set",
        "identity",
        "functor",
        "natural_transformation",
        "opposite_category",
        "product",
        "coproduct",
        "exponential_object",
    }
    assert required_keys.issubset(set(CATEGORY_THEORY_NOTATION.keys()))
    assert "alt_symbol" not in CATEGORY_THEORY_NOTATION["diagrammatic_composition"]
    assert CATEGORY_THEORY_NOTATION["monad_bind"]["class"] == "domain_specific_fp"


def test_cross_domain_mapping_frameworks():
    frameworks = {item["framework"] for item in CROSS_DOMAIN_MAPPINGS}
    expected_frameworks = {
        "Category Theory",
        "Set Theory",
        "Formal Logic",
        "Type Theory & Functional Programming",
        "Order Theory (Posets)",
        "Lambda Lang (Λ)",
    }
    assert frameworks == expected_frameworks


def test_canonical_ir_encoding_and_structure():
    obj_a = canonical_ir_encode("object", id="A")
    obj_b = canonical_ir_encode("object", id="B")

    assert obj_a == "O:A"
    assert obj_b == "O:B"

    m_f = canonical_ir_encode("morphism", src="A", tgt="B", label="f")
    m_g = canonical_ir_encode("morphism", src="B", tgt="C", label="g")

    assert m_f == "M:A:B:f"
    assert m_g == "M:B:C:g"

    comp = canonical_ir_encode("composition", m1=m_f, m2=m_g)
    assert comp == f"COMP({m_f},{m_g})"

    id_a = canonical_ir_encode("identity", obj="A")
    assert id_a == "ID(A)"

    func = canonical_ir_encode("functor", src_cat="C", tgt_cat="D")
    assert func == "F:C:D"

    nat_trans = canonical_ir_encode(
        "natural_transformation", src_fun="F", tgt_fun="G", label="alpha"
    )
    assert nat_trans == "NAT:F:G:alpha"


def test_proposal_source_and_items_file_references():
    source_file = Path("docs/proposals/active/notation-sets/source.md")
    items_file = Path("docs/proposals/active/notation-sets/ITEMS.md")
    mdx_file = Path("proposals/notation-sets.mdx")

    assert source_file.exists()
    assert items_file.exists()
    assert mdx_file.exists()

    source_text = source_file.read_text()
    items_text = items_file.read_text()
    mdx_text = mdx_file.read_text()

    for issue in ["#320", "#309", "#182", "#126", "#304", "#196", "#177", "#208", "#274"]:
        assert issue in source_text or issue in mdx_text

    for nse in ["NSE-020", "NSE-021", "NSE-022", "NSE-023"]:
        assert nse in items_text
        assert nse in mdx_text

    for fw in ["Set Theory", "Formal Logic", "Type Theory", "Order Theory", "Lambda Lang"]:
        assert fw in source_text

    assert "batteries_fork" in items_text or "batteries_fork" in source_text
