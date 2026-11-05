export type GraphViewMode = 'hierarchy' | 'network' | 'evidence';
export type GraphUrlState = {
  view: GraphViewMode;
  query: string;
  plane: string;
  edgeType: string;
  selected: string;
};
export function parseGraphUrlState(search: string): GraphUrlState;
