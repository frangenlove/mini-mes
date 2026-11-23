import { useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { fetchTickets } from "../api/tickets";
import { fetchMe } from "../api/auth";
import { useAuth } from "../auth/AuthContext";
import TicketDrawer from "../components/TicketDrawer";
import CreateTicketModal from "../components/CreateTicketModal";

const STATUS_LABEL: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  done: "已完成",
};

const SIZE = 10;

export default function TicketsPage() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [selectedId,setSelectedId] = useState<number | null >(null);
  const [creating, setCreating] = useState(false);
  const { logout } = useAuth();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["tickets", page, status],
    queryFn: () => fetchTickets({ page, size: SIZE, status: status || undefined }),
    placeholderData: keepPreviousData,
  });

  const { data: me}= useQuery({ queryKey: ["me"],queryFn: fetchMe});

  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1;

  return (
    <div className="page">
      <header>
        <h1>工单列表</h1>
        <button onClick={logout}>退出</button>
        <button onClick={ () => setCreating(true)}>+ 新建工单</button>
      </header>

      <div className="toolbar">
        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);                     // 换筛选必须回到第一页
          }}
        >
          <option value="">全部</option>
          <option value="pending">待处理</option>
          <option value="processing">处理中</option>
          <option value="done">已完成</option>
        </select>
        <span>共 {data?.total ?? 0} 条</span>
      </div>

      {isLoading && <p>加载中…</p>}
      {isError && <p className="error">{(error as Error).message}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th><th>标题</th><th>状态</th><th>优先级</th><th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map((t) => (
            <tr key={t.id} className="clickable" onClick={()=>setSelectedId(t.id)}>
              <td>{t.id}</td>
              <td>{t.title}</td>
              <td><span className={`badge ${t.status}`}>{STATUS_LABEL[t.status]}</span></td>
              <td>{t.priority}</td>
              <td>{new Date(t.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <footer>
        <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>上一页</button>
        <span>{page} / {totalPages}</span>
        <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>下一页</button>
      </footer>

      { selectedId !== null && (
        <TicketDrawer id={selectedId} canDelete={me?.role === "admin"} onClose={()=>setSelectedId(null)}/>
      )}

      { creating && <CreateTicketModal onClose={ () => setCreating(false)}></CreateTicketModal>}

    </div>
  );
}