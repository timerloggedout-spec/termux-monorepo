import { useEffect, useMemo, useRef, useState } from 'react';
import { hierarchy, tree } from 'd3-hierarchy';
import {
  Activity,
  ArrowDownToLine,
  ArrowUpFromLine,
  BookOpen,
  Check,
  ChevronDown,
  CircleHelp,
  Copy,
  Database,
  Download,
  ExternalLink,
  Filter,
  Focus,
  GitBranch,
  Layers3,
  Link2,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Table2,
  X,
} from 'lucide-react';

type Plane =
  | 'github'
  | 'x'
  | 'research-seeds'
  | 'papers'
  | 'following'
  | 'challenge';
type GraphNode = {
  id: string;
  label: string;
  kind: string;
  plane: Plane;
  parentId?: string;
  description: string;
  attributes?: Record<string, string>;
};
type Evidence = {
  plane: Plane;
  record: string;
  method: string;
  observed_at: string | null;
};
type GraphEdge = { src: string; dst: string; type: string; evidence: Evidence };
type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  source: string;
  importedAt?: string;
};
type ViewMode = 'hierarchy' | 'network' | 'evidence';

const fixture: GraphData = {
  source: 'Illustrative fixture · not live repository data',
  nodes: [
    {
      id: 'github:user:account',
      label: 'timerloggedout-spec',
      kind: 'user',
      plane: 'github',
      description:
        'Account node used to demonstrate actor-first repository relationships.',
    },
    {
      id: 'github:repository:termux-monorepo',
      label: 'termux-monorepo',
      kind: 'repository',
      plane: 'github',
      parentId: 'github:user:account',
      description:
        'Engineering and applied-research monorepo. This fixture does not read the live repository.',
      attributes: { visibility: 'public', role: 'management hub' },
    },
    {
      id: 'github:repository:studysprint',
      label: 'studysprint',
      kind: 'repository',
      plane: 'github',
      parentId: 'github:user:account',
      description: 'Example companion repository node.',
      attributes: { role: 'application' },
    },
    {
      id: 'topic:agentic-systems',
      label: 'agentic-systems',
      kind: 'topic',
      plane: 'github',
      parentId: 'github:repository:termux-monorepo',
      description: 'Illustrative topic classification.',
    },
    {
      id: 'topic:data-visualization',
      label: 'data-visualization',
      kind: 'topic',
      plane: 'github',
      parentId: 'github:repository:termux-monorepo',
      description: 'Illustrative topic classification.',
    },
    {
      id: 'domain:engineering',
      label: 'engineering',
      kind: 'domain',
      plane: 'github',
      parentId: 'github:repository:termux-monorepo',
      description: 'Domain nesting axis; domains remain nested, not flattened.',
    },
    {
      id: 'domain:research',
      label: 'research',
      kind: 'domain',
      plane: 'github',
      parentId: 'github:repository:studysprint',
      description: 'Illustrative domain classification.',
    },
    {
      id: 'github:research-seed:sample/graph-explorer',
      label: 'graph-explorer seed',
      kind: 'research-seed',
      plane: 'research-seeds',
      parentId: 'github:repository:termux-monorepo',
      description: 'Bridge record demonstrating a research-seed plane entity.',
    },
    {
      id: 'x:user:sample-handle',
      label: 'sample-handle',
      kind: 'user',
      plane: 'x',
      description:
        'Synthetic account node. No post text or private social content is represented.',
    },
    {
      id: 'x:tweet:sample-001',
      label: 'public signal · 001',
      kind: 'tweet',
      plane: 'x',
      parentId: 'x:user:sample-handle',
      description: 'Metadata-only example signal; no tweet text is stored.',
    },
    {
      id: 'challenge:event:sample-event',
      label: 'sample challenge',
      kind: 'event',
      plane: 'challenge',
      description: 'Synthetic challenge-plane event.',
    },
    {
      id: 'challenge:participant:sample-event/participant-a',
      label: 'participant A',
      kind: 'participant',
      plane: 'challenge',
      parentId: 'challenge:event:sample-event',
      description: 'Synthetic participant; no identity matching is implied.',
    },
    {
      id: 'challenge:project:sample-event/project-a',
      label: 'project A',
      kind: 'project',
      plane: 'challenge',
      parentId: 'challenge:event:sample-event',
      description: 'Synthetic project record.',
    },
    {
      id: 'paper:arxiv:reserved',
      label: 'papers · reserved',
      kind: 'paper-namespace',
      plane: 'papers',
      description:
        'Reserved namespace placeholder; no papers index is implied to exist.',
    },
  ],
  edges: [
    {
      src: 'github:user:account',
      dst: 'github:repository:termux-monorepo',
      type: 'owned',
      evidence: {
        plane: 'github',
        record: 'termux-monorepo',
        method: 'provenance_owned',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:user:account',
      dst: 'github:repository:studysprint',
      type: 'starred',
      evidence: {
        plane: 'github',
        record: 'studysprint',
        method: 'provenance_starred',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:repository:termux-monorepo',
      dst: 'github:user:account',
      type: 'authored_by',
      evidence: {
        plane: 'github',
        record: 'termux-monorepo',
        method: 'record_owner_field',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:repository:termux-monorepo',
      dst: 'topic:agentic-systems',
      type: 'about_topic',
      evidence: {
        plane: 'github',
        record: 'termux-monorepo',
        method: 'record_topics_field',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:repository:termux-monorepo',
      dst: 'topic:data-visualization',
      type: 'about_topic',
      evidence: {
        plane: 'github',
        record: 'termux-monorepo',
        method: 'record_topics_field',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:repository:termux-monorepo',
      dst: 'domain:engineering',
      type: 'in_domain',
      evidence: {
        plane: 'github',
        record: 'termux-monorepo',
        method: 'classification_domains',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:repository:studysprint',
      dst: 'domain:research',
      type: 'in_domain',
      evidence: {
        plane: 'github',
        record: 'studysprint',
        method: 'classification_domains',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'github:research-seed:sample/graph-explorer',
      dst: 'github:repository:termux-monorepo',
      type: 'upstream',
      evidence: {
        plane: 'research-seeds',
        record: 'graph-explorer',
        method: 'canonical_upstream',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'x:user:sample-handle',
      dst: 'x:tweet:sample-001',
      type: 'liked',
      evidence: {
        plane: 'x',
        record: 'sample-001',
        method: 'signals_liked',
        observed_at: null,
      },
    },
    {
      src: 'x:tweet:sample-001',
      dst: 'github:repository:termux-monorepo',
      type: 'mentions_repo',
      evidence: {
        plane: 'x',
        record: 'sample-001',
        method: 'public_url_reference',
        observed_at: null,
      },
    },
    {
      src: 'challenge:participant:sample-event/participant-a',
      dst: 'challenge:event:sample-event',
      type: 'competes_in',
      evidence: {
        plane: 'challenge',
        record: 'sample-event',
        method: 'participant_event_link',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'challenge:participant:sample-event/participant-a',
      dst: 'challenge:project:sample-event/project-a',
      type: 'entered_with',
      evidence: {
        plane: 'challenge',
        record: 'project-a',
        method: 'participant_project_link',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
    {
      src: 'challenge:project:sample-event/project-a',
      dst: 'challenge:event:sample-event',
      type: 'submitted_to',
      evidence: {
        plane: 'challenge',
        record: 'sample-event',
        method: 'project_submission_link',
        observed_at: '2026-10-29T10:55:00Z',
      },
    },
  ],
};

const planeLabels: Record<string, string> = {
  github: 'GitHub',
  x: 'X',
  'research-seeds': 'Research seeds',
  papers: 'Papers',
  following: 'Following',
  challenge: 'Challenge',
};
const kindColor: Record<string, string> = {
  user: '#9b8cff',
  repository: '#56b6a5',
  topic: '#e7b45f',
  domain: '#76a9e8',
  'research-seed': '#d38ac8',
  tweet: '#74a9d8',
  event: '#e38c72',
  participant: '#b0a0e8',
  project: '#83bd8d',
  'paper-namespace': '#9aa5b5',
};

function makeNodesFromEdges(edges: GraphEdge[]): GraphNode[] {
  const ids = Array.from(new Set(edges.flatMap(edge => [edge.src, edge.dst])));
  return ids.map(id => {
    const [plane, type, ...rest] = id.split(':');
    const label = rest.join(':').split('/').pop() || id;
    const kind = type || 'entity';
    return {
      id,
      label,
      kind,
      plane: (plane in planeLabels ? plane : 'github') as Plane,
      description:
        'Imported entity. Add richer node metadata through a nodes[] payload.',
    };
  });
}

function parseImport(files: File[]): GraphData {
  let nodes: GraphNode[] = [];
  let edges: GraphEdge[] = [];
  for (const file of files) {
    const text = '';
    void text;
  }
  throw new Error('Use the asynchronous import handler.');
}

function App() {
  const [data, setData] = useState<GraphData>(fixture);
  const [view, setView] = useState<ViewMode>('hierarchy');
  const [query, setQuery] = useState('');
  const [plane, setPlane] = useState('all');
  const [edgeType, setEdgeType] = useState('all');
  const [selected, setSelected] = useState('github:repository:termux-monorepo');
  const [showLabels, setShowLabels] = useState(true);
  const [message, setMessage] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const v = params.get('view');
    if (v === 'hierarchy' || v === 'network' || v === 'evidence') setView(v);
    setQuery(params.get('q') || '');
    setPlane(params.get('plane') || 'all');
    setEdgeType(params.get('edge') || 'all');
    if (params.get('node')) setSelected(params.get('node')!);
    const onPop = () => {
      const p = new URLSearchParams(window.location.search);
      const next = p.get('view');
      if (next === 'hierarchy' || next === 'network' || next === 'evidence')
        setView(next);
      setQuery(p.get('q') || '');
      setPlane(p.get('plane') || 'all');
      setEdgeType(p.get('edge') || 'all');
      if (p.get('node')) setSelected(p.get('node')!);
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  useEffect(() => {
    const p = new URLSearchParams();
    if (view !== 'hierarchy') p.set('view', view);
    if (query) p.set('q', query);
    if (plane !== 'all') p.set('plane', plane);
    if (edgeType !== 'all') p.set('edge', edgeType);
    if (selected) p.set('node', selected);
    const suffix = p.toString();
    window.history.replaceState(
      {},
      '',
      suffix ? `?${suffix}` : window.location.pathname
    );
  }, [view, query, plane, edgeType, selected]);

  const filteredNodes = useMemo(
    () =>
      data.nodes.filter(n => {
        const matchesPlane = plane === 'all' || n.plane === plane;
        const haystack = `${n.label} ${n.id} ${n.description}`.toLowerCase();
        return matchesPlane && haystack.includes(query.toLowerCase());
      }),
    [data.nodes, plane, query]
  );

  const visibleIds = useMemo(
    () => new Set(filteredNodes.map(n => n.id)),
    [filteredNodes]
  );
  const filteredEdges = useMemo(
    () =>
      data.edges.filter(
        e =>
          visibleIds.has(e.src) &&
          visibleIds.has(e.dst) &&
          (edgeType === 'all' || e.type === edgeType)
      ),
    [data.edges, visibleIds, edgeType]
  );
  const selectedNode =
    data.nodes.find(n => n.id === selected) ||
    filteredNodes[0] ||
    data.nodes[0];
  const selectedEdges = data.edges.filter(
    e => e.src === selectedNode?.id || e.dst === selectedNode?.id
  );
  const planes = Array.from(new Set(data.nodes.map(n => n.plane)));
  const edgeTypes = Array.from(new Set(data.edges.map(e => e.type))).sort();

  const importFiles = async (files: FileList | null) => {
    if (!files?.length) return;
    try {
      const incomingNodes: GraphNode[] = [];
      const incomingEdges: GraphEdge[] = [];
      for (const file of Array.from(files)) {
        const raw = await file.text();
        if (file.name.endsWith('.jsonl') || file.name.endsWith('.ndjson')) {
          for (const [index, line] of raw.split(/\r?\n/).entries()) {
            if (!line.trim()) continue;
            let item: any;
            try {
              item = JSON.parse(line);
            } catch {
              throw new Error(
                `Invalid JSON on line ${index + 1} of ${file.name}`
              );
            }
            if (
              !item.src ||
              !item.dst ||
              !item.type ||
              !item.evidence?.plane ||
              !item.evidence?.record ||
              !item.evidence?.method ||
              !('observed_at' in item.evidence)
            ) {
              throw new Error(
                `Line ${index + 1} does not satisfy graph-edges/v1 required fields.`
              );
            }
            incomingEdges.push(item as GraphEdge);
          }
        } else if (file.name.endsWith('.json')) {
          const payload = JSON.parse(raw);
          if (Array.isArray(payload)) incomingEdges.push(...payload);
          else {
            if (Array.isArray(payload.nodes))
              incomingNodes.push(...payload.nodes);
            if (Array.isArray(payload.edges))
              incomingEdges.push(...payload.edges);
          }
        } else {
          throw new Error(`Unsupported file: ${file.name}. Use JSON or JSONL.`);
        }
      }
      if (!incomingEdges.length)
        throw new Error(
          'No edge records found. Select edges.jsonl or a JSON object containing edges[].'
        );
      const inferred = makeNodesFromEdges(incomingEdges);
      const nodeMap = new Map(
        [...inferred, ...incomingNodes].map(n => [n.id, n])
      );
      const imported: GraphData = {
        nodes: Array.from(nodeMap.values()),
        edges: incomingEdges,
        source: `Imported locally · ${Array.from(files)
          .map(f => f.name)
          .join(', ')}`,
        importedAt: new Date().toISOString(),
      };
      setData(imported);
      setSelected(imported.nodes[0]?.id || '');
      setMessage(
        `Imported ${imported.nodes.length} entities and ${imported.edges.length} relationships. Source files remain in your browser.`
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Import failed.');
    } finally {
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const exportSvg = () => {
    if (!svgRef.current) return;
    const clone = svgRef.current.cloneNode(true) as SVGSVGElement;
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('width', '1200');
    clone.setAttribute('height', '760');
    const source = new XMLSerializer().serializeToString(clone);
    const url = URL.createObjectURL(
      new Blob([source], { type: 'image/svg+xml;charset=utf-8' })
    );
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'graph-explorer.svg';
    anchor.click();
    URL.revokeObjectURL(url);
    setMessage('SVG export prepared.');
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setMessage('Shareable view link copied.');
    } catch {
      setMessage(
        'Copy is unavailable in this browser. Copy the URL from the address bar.'
      );
    }
  };

  const reset = () => {
    setView('hierarchy');
    setQuery('');
    setPlane('all');
    setEdgeType('all');
    setSelected('github:repository:termux-monorepo');
    setMessage('View reset.');
  };

  const hierarchyRoot = useMemo(() => {
    const byId = new Map(
      data.nodes.map(n => [n.id, { ...n, children: [] as any[] }])
    );
    const roots: any[] = [];
    byId.forEach(node => {
      const parent = node.parentId ? byId.get(node.parentId) : undefined;
      if (parent) parent.children.push(node);
      else roots.push(node);
    });
    const wrap = { id: 'root', label: 'Graph entities', children: roots };
    return hierarchy(wrap, d => d.children);
  }, [data.nodes]);

  const hierarchyLayout = useMemo(
    () => tree<any>().size([650, 1050])(hierarchyRoot),
    [hierarchyRoot]
  );
  const hierarchyPoints = hierarchyLayout
    .descendants()
    .filter(d => d.data.id !== 'root' && visibleIds.has(d.data.id));
  const hierarchyLinks = hierarchyLayout
    .links()
    .filter(
      l =>
        l.source.data.id !== 'root' &&
        visibleIds.has(l.source.data.id) &&
        visibleIds.has(l.target.data.id)
    );

  const networkPoints = useMemo(() => {
    const nodes = filteredNodes;
    const cx = 520,
      cy = 325,
      radius = Math.min(255, 100 + nodes.length * 8);
    return nodes.map((node, index) => {
      const angle =
        (index / Math.max(nodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
      return {
        node,
        x: cx + Math.cos(angle) * radius,
        y: cy + Math.sin(angle) * radius,
      };
    });
  }, [filteredNodes]);
  const networkById = new Map(networkPoints.map(p => [p.node.id, p]));

  const showNode = (id: string) => setSelected(id);
  const svgTitle =
    view === 'hierarchy'
      ? 'Entity hierarchy'
      : view === 'network'
        ? 'Relationship network'
        : 'Evidence timeline';

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Layers3 size={19} />
          </div>
          <div>
            <strong>Graph Studio</strong>
            <small>PARALLEL TRACK · v0.1.0</small>
          </div>
        </div>
        <div className="side-label">WORKSPACE</div>
        <button className="nav active">
          <Network size={16} /> Explorer <span>⌘1</span>
        </button>
        <button className="nav" onClick={() => setView('evidence')}>
          <ShieldCheck size={16} /> Evidence ledger
        </button>
        <button
          className="nav"
          onClick={() =>
            setMessage(
              'Dataset controls are available in the import and filter bar.'
            )
          }
        >
          <Database size={16} /> Dataset
        </button>
        <div className="side-divider" />
        <div className="side-label">DATA PLANES</div>
        {planes.map(p => (
          <button
            className="plane-item"
            key={p}
            onClick={() => setPlane(plane === p ? 'all' : p)}
          >
            <span
              className="plane-dot"
              style={{
                background:
                  p === 'github'
                    ? '#65b7a7'
                    : p === 'challenge'
                      ? '#d88f7b'
                      : p === 'x'
                        ? '#83aee0'
                        : '#b49be8',
              }}
            />
            {planeLabels[p] || p}
            <span className="plane-count">
              {data.nodes.filter(n => n.plane === p).length}
            </span>
          </button>
        ))}
        <div className="sidebar-bottom">
          <div className="status-line">
            <span className="live-dot" /> LOCAL DATA MODE
          </div>
          <small>
            Read-only graph view
            <br />
            No source indexes are modified.
          </small>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="crumb">
            <span>termux-monorepo</span>
            <span className="slash">/</span>
            <strong>Graph Explorer</strong>
            <span className="version">v0.1.0</span>
          </div>
          <div className="top-actions">
            <button className="ghost-btn" onClick={copyLink}>
              <Link2 size={15} /> Share view
            </button>
            <button
              className="primary-btn"
              onClick={() => fileRef.current?.click()}
            >
              <ArrowUpFromLine size={15} /> Import graph
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".json,.jsonl,.ndjson,application/json"
              multiple
              hidden
              onChange={e => importFiles(e.target.files)}
            />
          </div>
        </header>

        <section className="intro">
          <div>
            <div className="eyebrow">
              <Sparkles size={13} /> INDEPENDENT VISUALIZATION TRACK
            </div>
            <h1>
              See the connections.
              <br />
              <span>Keep the evidence.</span>
            </h1>
            <p>
              A renderer-independent graph workspace for exploring entities,
              relationships and provenance across observation planes.
            </p>
          </div>
          <div className="intro-note">
            <div className="note-icon">
              <BookOpen size={17} />
            </div>
            <div>
              <strong>Derived view, not source of truth</strong>
              <p>
                Import committed indexes to explore them. Original collectors
                and single-writer ownership stay untouched.
              </p>
            </div>
          </div>
        </section>

        <div className="metrics">
          <div className="metric">
            <span>ENTITIES</span>
            <strong>{filteredNodes.length.toLocaleString()}</strong>
            <small>in current view</small>
          </div>
          <div className="metric">
            <span>RELATIONSHIPS</span>
            <strong>{filteredEdges.length.toLocaleString()}</strong>
            <small>visible edges</small>
          </div>
          <div className="metric">
            <span>OBSERVATION PLANES</span>
            <strong>{new Set(filteredNodes.map(n => n.plane)).size}</strong>
            <small>represented</small>
          </div>
          <div className="metric">
            <span>PROVENANCE COVERAGE</span>
            <strong>{filteredEdges.length ? '100%' : '—'}</strong>
            <small>all imported edges carry evidence</small>
          </div>
        </div>

        <section className="workspace">
          <div className="workspace-head">
            <div>
              <div className="section-kicker">EXPLORATION CANVAS</div>
              <h2>{svgTitle}</h2>
              <p>{data.source}</p>
            </div>
            <div className="canvas-actions">
              <div className="view-switch" role="group" aria-label="Graph view">
                <button
                  className={view === 'hierarchy' ? 'selected' : ''}
                  onClick={() => setView('hierarchy')}
                  aria-pressed={view === 'hierarchy'}
                >
                  <GitBranch size={15} /> Hierarchy
                </button>
                <button
                  className={view === 'network' ? 'selected' : ''}
                  onClick={() => setView('network')}
                  aria-pressed={view === 'network'}
                >
                  <Network size={15} /> Network
                </button>
                <button
                  className={view === 'evidence' ? 'selected' : ''}
                  onClick={() => setView('evidence')}
                  aria-pressed={view === 'evidence'}
                >
                  <Activity size={15} /> Evidence
                </button>
              </div>
              <button
                className="icon-btn"
                title="Export SVG"
                aria-label="Export SVG"
                onClick={exportSvg}
              >
                <Download size={16} />
              </button>
              <button
                className="icon-btn"
                title="Reset view"
                aria-label="Reset view"
                onClick={reset}
              >
                <Focus size={16} />
              </button>
            </div>
          </div>

          <div className="filter-row">
            <label className="searchbox">
              <Search size={16} />
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Search entities, IDs, descriptions…"
                aria-label="Search graph"
              />
              {query && (
                <button onClick={() => setQuery('')} aria-label="Clear search">
                  <X size={14} />
                </button>
              )}
            </label>
            <label className="filter-select">
              <Filter size={14} />
              <select
                value={plane}
                onChange={e => setPlane(e.target.value)}
                aria-label="Filter by plane"
              >
                <option value="all">All planes</option>
                {planes.map(p => (
                  <option value={p} key={p}>
                    {planeLabels[p] || p}
                  </option>
                ))}
              </select>
              <ChevronDown size={13} />
            </label>
            <label className="filter-select">
              <select
                value={edgeType}
                onChange={e => setEdgeType(e.target.value)}
                aria-label="Filter by relationship"
              >
                <option value="all">All relationships</option>
                {edgeTypes.map(t => (
                  <option value={t} key={t}>
                    {t}
                  </option>
                ))}
              </select>
              <ChevronDown size={13} />
            </label>
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={showLabels}
                onChange={e => setShowLabels(e.target.checked)}
              />{' '}
              Labels
            </label>
          </div>

          <div className="canvas-layout">
            <aside className="outline-panel">
              <div className="panel-title">
                ENTITY OUTLINE <span>{filteredNodes.length}</span>
              </div>
              <div className="outline-list">
                {filteredNodes.map(n => (
                  <button
                    key={n.id}
                    className={
                      selectedNode?.id === n.id
                        ? 'outline-item chosen'
                        : 'outline-item'
                    }
                    onClick={() => showNode(n.id)}
                  >
                    <span
                      className="kind-dot"
                      style={{ background: kindColor[n.kind] || '#91a2b7' }}
                    />
                    <span className="outline-text">
                      <strong>{n.label}</strong>
                      <small>{n.kind}</small>
                    </span>
                  </button>
                ))}
                {!filteredNodes.length && (
                  <p className="empty-text">No entities match these filters.</p>
                )}
              </div>
            </aside>

            <div className="graph-stage">
              {view === 'evidence' ? (
                <div className="evidence-list">
                  {filteredEdges
                    .slice()
                    .sort((a, b) =>
                      (b.evidence.observed_at || '').localeCompare(
                        a.evidence.observed_at || ''
                      )
                    )
                    .map((edge, i) => (
                      <button
                        className="evidence-row"
                        key={i}
                        onClick={() => showNode(edge.src)}
                      >
                        <div className="evidence-type">{edge.type}</div>
                        <div className="evidence-route">
                          <strong>
                            {data.nodes.find(n => n.id === edge.src)?.label ||
                              edge.src}
                          </strong>
                          <span>→</span>
                          <strong>
                            {data.nodes.find(n => n.id === edge.dst)?.label ||
                              edge.dst}
                          </strong>
                        </div>
                        <div className="evidence-meta">
                          <span>{planeLabels[edge.evidence.plane]}</span>
                          <span>{edge.evidence.method}</span>
                          <span>
                            {edge.evidence.observed_at
                              ? new Date(
                                  edge.evidence.observed_at
                                ).toLocaleString()
                              : 'Timestamp unavailable'}
                          </span>
                        </div>
                      </button>
                    ))}
                  {!filteredEdges.length && (
                    <div className="empty-canvas">
                      <CircleHelp size={24} />
                      <strong>No evidence in this slice</strong>
                      <span>Try a broader plane or relationship filter.</span>
                    </div>
                  )}
                </div>
              ) : (
                <svg
                  ref={svgRef}
                  className="graph-svg"
                  viewBox="0 0 1100 690"
                  role="img"
                  aria-labelledby="graph-title graph-desc"
                >
                  <title id="graph-title">{svgTitle}</title>
                  <desc id="graph-desc">
                    Interactive graph with {filteredNodes.length} visible
                    entities and {filteredEdges.length} visible evidence-backed
                    relationships. Select a node to inspect its provenance.
                  </desc>
                  <defs>
                    <pattern
                      id="dots"
                      width="24"
                      height="24"
                      patternUnits="userSpaceOnUse"
                    >
                      <circle
                        cx="1"
                        cy="1"
                        r="1"
                        fill="#344256"
                        opacity=".55"
                      />
                    </pattern>
                  </defs>
                  <rect width="1100" height="690" fill="url(#dots)" />
                  {view === 'hierarchy' ? (
                    <>
                      <g transform="translate(35 15)">
                        {hierarchyLinks.map((link, i) => (
                          <path
                            key={i}
                            d={`M${link.source.y},${link.source.x} C${(link.source.y + link.target.y) / 2},${link.source.x} ${(link.source.y + link.target.y) / 2},${link.target.x} ${link.target.y},${link.target.x}`}
                            fill="none"
                            stroke="#52647b"
                            strokeWidth="1.4"
                            opacity=".8"
                          />
                        ))}
                        {hierarchyPoints.map(point => {
                          const n = point.data as GraphNode;
                          const active = selectedNode?.id === n.id;
                          return (
                            <g
                              key={n.id}
                              transform={`translate(${point.y},${point.x})`}
                              className="svg-node"
                              role="button"
                              tabIndex={0}
                              aria-label={`Select ${n.label}, ${n.kind}`}
                              onClick={() => showNode(n.id)}
                              onKeyDown={e => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  showNode(n.id);
                                }
                              }}
                            >
                              <circle
                                r={active ? 9 : 7}
                                fill={kindColor[n.kind] || '#91a2b7'}
                                stroke={active ? '#fff' : '#172333'}
                                strokeWidth={active ? 2.5 : 1.5}
                              />
                              {showLabels && (
                                <text
                                  x="13"
                                  y="4"
                                  className={
                                    active
                                      ? 'node-label active-label'
                                      : 'node-label'
                                  }
                                >
                                  {n.label}
                                </text>
                              )}
                            </g>
                          );
                        })}
                      </g>
                    </>
                  ) : (
                    <>
                      {filteredEdges.map((edge, i) => {
                        const a = networkById.get(edge.src),
                          b = networkById.get(edge.dst);
                        if (!a || !b) return null;
                        return (
                          <g key={i}>
                            <line
                              x1={a.x}
                              y1={a.y}
                              x2={b.x}
                              y2={b.y}
                              stroke="#63758b"
                              strokeWidth="1.5"
                              opacity=".55"
                            />
                            <text
                              x={(a.x + b.x) / 2}
                              y={(a.y + b.y) / 2 - 5}
                              className="edge-label"
                            >
                              {edge.type}
                            </text>
                          </g>
                        );
                      })}
                      {networkPoints.map(({ node: n, x, y }) => {
                        const active = selectedNode?.id === n.id;
                        return (
                          <g
                            key={n.id}
                            transform={`translate(${x},${y})`}
                            className="svg-node"
                            role="button"
                            tabIndex={0}
                            aria-label={`Select ${n.label}, ${n.kind}`}
                            onClick={() => showNode(n.id)}
                            onKeyDown={e => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                showNode(n.id);
                              }
                            }}
                          >
                            <circle
                              r={active ? 13 : 10}
                              fill={kindColor[n.kind] || '#91a2b7'}
                              stroke={active ? '#fff' : '#172333'}
                              strokeWidth={active ? 3 : 2}
                            />
                            {showLabels && (
                              <text
                                x="15"
                                y="4"
                                className={
                                  active
                                    ? 'node-label active-label'
                                    : 'node-label'
                                }
                              >
                                {n.label}
                              </text>
                            )}
                          </g>
                        );
                      })}
                    </>
                  )}
                </svg>
              )}
              <div className="canvas-legend">
                <span>
                  <i style={{ background: '#9b8cff' }} /> Actor
                </span>
                <span>
                  <i style={{ background: '#56b6a5' }} /> Repository
                </span>
                <span>
                  <i style={{ background: '#e7b45f' }} /> Topic
                </span>
                <span>
                  <i style={{ background: '#76a9e8' }} /> Domain
                </span>
                <span className="legend-hint">
                  Select a node to inspect · keyboard: Tab then Enter
                </span>
              </div>
            </div>

            <aside className="inspector">
              <div className="panel-title">
                INSPECTOR <span>DETAILS</span>
              </div>
              {selectedNode ? (
                <>
                  <div className="inspector-kind">
                    <span
                      className="kind-dot large"
                      style={{
                        background: kindColor[selectedNode.kind] || '#91a2b7',
                      }}
                    />
                    {selectedNode.kind}
                  </div>
                  <h3>{selectedNode.label}</h3>
                  <div className="entity-id">{selectedNode.id}</div>
                  <p className="entity-description">
                    {selectedNode.description}
                  </p>
                  <div className="detail-divider" />
                  <div className="detail-label">OBSERVATION PLANE</div>
                  <div className="detail-value">
                    {planeLabels[selectedNode.plane]}
                  </div>
                  {Object.entries(selectedNode.attributes || {}).map(
                    ([k, v]) => (
                      <div key={k} className="attribute">
                        <span>{k}</span>
                        <strong>{v}</strong>
                      </div>
                    )
                  )}
                  <div className="detail-divider" />
                  <div className="detail-label">
                    CONNECTED EVIDENCE <b>{selectedEdges.length}</b>
                  </div>
                  {selectedEdges.slice(0, 8).map((edge, i) => (
                    <button
                      className="connected-item"
                      key={i}
                      onClick={() => setEdgeType(edge.type)}
                    >
                      <span className="connection-arrow">
                        {edge.src === selectedNode.id ? '→' : '←'}
                      </span>
                      <span>
                        <strong>{edge.type}</strong>
                        <small>
                          {edge.src === selectedNode.id ? edge.dst : edge.src}
                        </small>
                      </span>
                    </button>
                  ))}
                  {!selectedEdges.length && (
                    <p className="empty-text">
                      No relationships for this entity in the current dataset.
                    </p>
                  )}
                </>
              ) : (
                <p className="empty-text">
                  Select an entity to inspect its details.
                </p>
              )}
            </aside>
          </div>
          <div className="canvas-foot">
            <span>
              <span className="live-dot" />{' '}
              {data.importedAt ? 'IMPORTED DATA' : 'DEMO FIXTURE'}
            </span>
            <span>
              Read-only · actor-first edges · source provenance retained
            </span>
            <button onClick={exportSvg}>
              <ArrowDownToLine size={13} /> Export SVG
            </button>
          </div>
        </section>

        <section className="lower-grid">
          <div className="lower-card">
            <div className="lower-icon">
              <ShieldCheck size={17} />
            </div>
            <div>
              <strong>Evidence stays attached</strong>
              <p>
                Every relationship keeps its plane, source record, derivation
                method and observed timestamp. Missing timestamps remain
                missing.
              </p>
            </div>
          </div>
          <div className="lower-card">
            <div className="lower-icon">
              <Layers3 size={17} />
            </div>
            <div>
              <strong>Planes stay independent</strong>
              <p>
                Import is local and read-only. No graph view can write back to
                an upstream observation index.
              </p>
            </div>
          </div>
          <div className="lower-card">
            <div className="lower-icon">
              <Table2 size={17} />
            </div>
            <div>
              <strong>Explore without losing context</strong>
              <p>
                Search, filters, selection and view mode are encoded in the URL.
                Export the current SVG for review.
              </p>
            </div>
          </div>
        </section>

        <footer>
          <span>GRAPH STUDIO · PARALLEL RELEASE 0.1.0</span>
          <span>SVG2 · D3 HIERARCHY · LOCAL-FIRST</span>
        </footer>
      </main>
      {message && (
        <div className="toast" role="status">
          <Check size={15} />
          {message}
          <button onClick={() => setMessage('')} aria-label="Dismiss message">
            <X size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
