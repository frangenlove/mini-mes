import client from "./client";
import type { User } from "../types"

export async function fetchMe(){
    const { data } =await client.get<User>("/auth/me");
    return data;
}