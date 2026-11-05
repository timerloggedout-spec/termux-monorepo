export type GraphPlane = 'github' | 'x' | 'research-seeds' | 'papers' | 'following' | 'challenge';
export type ImportedNode = {
  id: string;
  label: string;
  kind: string;
  plane: GraphPlane;
  parentId?: string;
  description: string;
  attributes: Record<string, string>;
};
export type ImportedEdge = {
  src: string;
  dst: string;
  type: string;
  evidence: {
    plane: GraphPlane;
    record: string;
    method: string;
    observed_at: string | null;
  };
};
export function parseGraphImport(raw: string, fileName: string): {
  nodes: ImportedNode[];
  edges: ImportedEdge[];
};
