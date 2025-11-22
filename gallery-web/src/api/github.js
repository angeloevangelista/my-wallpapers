import axios from "axios";

const OWNER = "angeloevangelista";
const REPO = "my-wallpapers";

export const fetchImagesFromFolder = async (folder) => {
  const url = `https://api.github.com/repos/${OWNER}/${REPO}/contents/${folder}`;
  try {
    const response = await axios.get(url);
    return response.data.filter(file =>
      file.name.match(/\.(jpg|jpeg|png|gif|bmp|webp)$/i)
    );
  } catch (err) {
    console.error("GitHub fetch failed:", err);
    return [];
  }
};