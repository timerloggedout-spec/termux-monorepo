const SUPPORTED_PLANES = new Set([
  'github', 'x', 'research-seeds', 'papers', 'following', 'challenge',
]);

export function parseGraphUrlState(search) {
  const params = new URLSearchParams(search);
  const requestedView = params.get('view');
  const requestedPlane = params.get('plane');
  return {
    view: ['hierarchy', 'network', 'evidence'].includes(requestedView)
      ? requestedView
      : 'hierarchy',
    query: params.get('q') || '',
    plane:
      requestedPlane === 'all' || SUPPORTED_PLANES.has(requestedPlane)
        ? requestedPlane
        : 'all',
    edgeType: params.get('edge') || 'all',
    selected: params.get('node') || 'github:repository:termux-monorepo',
  };
}
