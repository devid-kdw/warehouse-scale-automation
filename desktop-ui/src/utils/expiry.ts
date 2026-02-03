import dayjs from 'dayjs';

/**
 * Expiry status types:
 * - 'expired': Date is in the past
 * - 'soon': Date is within 30 days
 * - 'ok': Date is > 30 days in future
 * - 'none': Date is invalid or null
 */
export type ExpiryStatus = 'expired' | 'soon' | 'ok' | 'none';

/**
 * Returns the status of an expiry date.
 * @param dateStr ISO date string or Date object
 * @param warningThresholdDays Days threshold for 'soon' warning (default 30)
 */
export function getExpiryStatus(dateStr: string | Date | undefined | null, warningThresholdDays = 30): ExpiryStatus {
    if (!dateStr) return 'none';

    const expiry = dayjs(dateStr);
    if (!expiry.isValid()) return 'none';

    const now = dayjs();
    const today = now.startOf('day');
    const expiryDate = expiry.startOf('day');

    if (expiryDate.isBefore(today)) {
        return 'expired';
    }

    if (expiryDate.diff(today, 'day') <= warningThresholdDays) {
        return 'soon';
    }

    return 'ok';
}
