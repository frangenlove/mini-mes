export type TicketStatus = "pending" | "processing" | "done"

export interface Ticket {
    id: number;
    title: string;
    description: string | null,
    status: TicketStatus;
    priority: number;
    created_by: number;
    created_at: string;
    updated_at: string | null;
}

export interface Page<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
}