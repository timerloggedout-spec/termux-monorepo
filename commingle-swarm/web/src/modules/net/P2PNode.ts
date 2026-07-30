export class P2PNode {
  constructor(private opts: { trackers: string[] }) {}
  async start() {
    // Placeholder for WebRTC/WebTorrent bootstrap
    console.log('P2PNode start with trackers:', this.opts.trackers);
  }
  async publish(topic: string, payload: any) {
    console.log('Publish', topic, payload);
  }
  async subscribe(topic: string, handler: (msg: any) => void) {
    console.log('Subscribe', topic);
  }
}
