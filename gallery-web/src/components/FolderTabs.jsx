export default function FolderTabs({ current, onChange }) {
  const folders = ["wallpapers", "rejected"];
  return (
    <div className="folder-tabs">
      {folders.map(folder => (
        <button
          key={folder}
          className={`folder-btn ${current===folder?"active":""}`}
          onClick={()=>onChange(folder)}
        >
          {folder.toUpperCase()}
        </button>
      ))}
    </div>
  );
}