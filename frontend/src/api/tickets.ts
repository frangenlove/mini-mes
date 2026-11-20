import client from "./client"
import type {Page,Ticket} from "../types"

export async function fetchTickets(params: {
    page: number;
    size: number;
    status?: string;
}){
    const { data } = await client.get<Page<Ticket>>("/tickets",{params});
    return data;
}
