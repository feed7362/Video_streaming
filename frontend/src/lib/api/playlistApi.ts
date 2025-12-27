import clientApi from "./clientApi";
import type { Playlist, PlaylistPreview } from "./types";

export const createPlaylist = (
  name: string,
  isPublic: boolean,
): Promise<Playlist> =>
  clientApi
    .post<Playlist>("/playlists", { name, isPublic })
    .then((res) => res.data);

export const getPlaylists = (): Promise<PlaylistPreview[]> =>
  clientApi.get<PlaylistPreview[]>("/playlists").then((res) => res.data);

export const addToPlaylist = (
  playlistId: string,
  videoId: string,
): Promise<void> =>
  clientApi.post(`/playlists/${playlistId}/videos`, { videoId }).then(() => {});

export const deleteFromPlaylist = (
  playlistId: string,
  videoId: string,
): Promise<void> =>
  clientApi.delete(`/playlists/${playlistId}/videos/${videoId}`).then(() => {});

export const deletePlaylist = (playlistId: string): Promise<void> =>
  clientApi.delete(`/playlists/${playlistId}`).then(() => {});

export default {
  createPlaylist,
  getPlaylists,
  addToPlaylist,
  deleteFromPlaylist,
  deletePlaylist,
};
