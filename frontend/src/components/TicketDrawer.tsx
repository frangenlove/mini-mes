import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "../api/client";
import type { TicketStatus } from "../types";
import { fetchTicket } from "../api/tickets";

const STATUS_LABEL: Record<TicketStatus, string> = {
  pending: "待处理",
  processing: "处理中",
  done: "已完成",
};

const NEXT_STEP: Record<TicketStatus, { to: TicketStatus; label: string } | null> = {
    pending: {to: "processing", label: "开始处理"},
    processing: {to: "done", label: "完成"},
    done: null
};

type Props = {
    id: number;
    canDelete: boolean;
    onClose: () => void;
}

export default function TicketDrawer( { id,onClose,canDelete }: Props){
    const queryClient = useQueryClient();

    const { data: ticket,isLoading} = useQuery({
        queryKey: ["ticket",id],
        queryFn: () => fetchTicket(id)
    });

    
    const mutation = useMutation({
        mutationFn: (status: string) => client.patch(`tickets/${id}`,{ status }),
        onSuccess: () => {
            queryClient.invalidateQueries( {queryKey: ["ticket",id]});
            queryClient.invalidateQueries( {queryKey: ["tickets"]});
        }
    });

    const deleteMutation = useMutation({
        mutationFn: () => client.delete(`tickets/${id}`),
        onSuccess: () => {
            queryClient.invalidateQueries( {queryKey: ["tickets"]});
            onClose();
        }
    });

    if (isLoading || !ticket) return <div className="drawer">加载中...</div>

    const next = NEXT_STEP[ticket.status];

    return (
        <div className="drawer" onClick={onClose}>
            <aside className="drawer-panel" onClick={(e)=>e.stopPropagation()}>
                <header>
                    <h2>工单 #{ticket.id}</h2>
                    <button onClick={onClose}></button>
                </header>

                <dl>
                    <dt>标题</dt><dd>{ticket.title}</dd>
                    <dt>描述</dt><dd>{ticket.description || "-"}</dd>
                    <dt>状态</dt><dd>{STATUS_LABEL[ticket.status]}</dd>
                    <dt>优先级</dt><dd>{ticket.priority}</dd>
                </dl>

                { next && (
                    <button disabled={mutation.isPending} onClick={() => mutation.mutate(next.to)}>
                        {mutation.isPending ? "处理中..." : next.label}
                    </button>
                )}
                { canDelete && (
                    <button
                        className="danger"
                        disabled={deleteMutation.isPending}
                        onClick={() => {
                            if (confirm("确定删除这条工单？")) deleteMutation.mutate();
                        }}
                    >
                        删除
                    </button>
                )}
                { mutation.isError && <p className="error">操作失败，请重试</p>}
            </aside>
        </div>
    );

};