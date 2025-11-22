import { useState } from "react";
import FolderTabs from "./components/FolderTabs";
import Gallery from "./components/Gallery";

export default function App() {
  const [folder, setFolder] = useState("wallpapers");

  return (
    <div className="container">
      <h1>My Wallpapers</h1>

      <FolderTabs current={folder} onChange={setFolder} />

      <Gallery folder={folder} />
    </div>
  );
}