import { BrowserRouter, Navigate,Route,Routes} from "react-router-dom"
import { AuthProvider,useAuth } from './auth/AuthContext'
import LoginPage from "./pages/LoginPage"
import TicketsPage from "./pages/TicketsPage"

function Protected({children}: {children: React.ReactNode}){
  const { token } = useAuth();
  return token ? <>{children}</> : <Navigate to = "/login" replace/>
}

export default function App(){
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="login" element={<LoginPage/>}/>
          <Route path="/" element={<Protected><TicketsPage/></Protected>}/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}