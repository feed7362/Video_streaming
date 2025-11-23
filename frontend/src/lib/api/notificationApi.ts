import clientApi from "./clientApi";
import type { Notification } from '../../types/notification';

export const getNotifications = (): Promise<Notification[]> =>
    clientApi.get<Notification[]>('/notifications').then(res => res.data);

export const markNotificationAsRead = (notificationId: string): Promise<void> =>
    clientApi.put(`/notifications/${notificationId}/read`).then(() => { });

export default { getNotifications, markNotificationAsRead };
