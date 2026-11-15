import { Chat } from "./chat";

// One demo store for now. Multi-store routing comes with tenants (E2).
export default function Home() {
  return <Chat storeSlug="momo-mart" storeName="Momo Mart" />;
}
