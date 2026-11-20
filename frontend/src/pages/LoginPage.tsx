import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // ⚠️ 登录接口收的是表单，不是 JSON —— 和后端 OAuth2PasswordRequestForm 对齐
      const body = new URLSearchParams({ username, password });
      const { data } = await client.post<{ access_token: string }>("/auth/login", body);
      login(data.access_token);
      navigate("/", { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.error?.message ?? "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="center">
      <form className="card" onSubmit={onSubmit}>
        <h2>Mini-MES 登录</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="用户名" />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="密码"
        />
        {error && <p className="error">{error}</p>}
        <button disabled={loading}>{loading ? "登录中…" : "登录"}</button>
      </form>
    </div>
  );
}