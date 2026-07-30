export class IpfsStore {
  constructor(private api: string) {}
  async publish(obj: any) {
    // Placeholder: return fake CID
    const cid = 'bafy' + Math.random().toString(36).slice(2, 10);
    console.log('Published to IPFS', cid);
    return cid;
  }
}
