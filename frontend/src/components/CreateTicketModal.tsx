import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import client from "../api/client";

type Props = { onClose: () => void };

export default function CreateTicketModal({ onClose }: Props) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState(3);

  const mutation = useMutation({
    mutationFn: (payload: { title: string; priority: number }) =>
      client.post("/tickets", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      onClose();
    },
  });

  return (
    <div className="drawer" onClick={onClose}>
      <form
        className="drawer-panel"
        onClick={(e) => e.stopPropagation()}
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate({ title, priority });
        }}
      >
        <header>
          <h2>新建工单</h2>
          <button type="button" onClick={onClose}>×</button>
        </header>

        <label>
          标题
          <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </label>

        <label>
          优先级
          <select value={priority} onChange={(e) => setPriority(Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>

        {mutation.isError && <p className="error">创建失败</p>}
        <button disabled={mutation.isPending || !title.trim()}>
          {mutation.isPending ? "提交中…" : "创建"}
        </button>
      </form>
    </div>
  );
}