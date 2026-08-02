import { Link, useLocation } from "wouter"
import { Users, LayoutDashboard, Settings, Radio, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "../ui/button"

export function Sidebar() {
  const [location, setLocation] = useLocation()
  
  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Users", href: "/users", icon: Users },
    { name: "Settings", href: "/settings", icon: Settings },
    { name: "Broadcast", href: "/broadcast", icon: Radio },
  ]

  const handleLogout = () => {
    localStorage.removeItem("admin_token")
    setLocation("/login")
  }

  return (
    <>
      {/* ── Desktop sidebar ── */}
      <div className="hidden md:flex h-screen w-64 flex-col border-r bg-card shadow-sm fixed top-0 left-0 z-10">
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-primary tracking-tight">1WIN Bot Admin</h1>
        </div>
        <div className="flex-1 py-6 px-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location === item.href
            return (
              <Link key={item.href} href={item.href} className="block">
                <div
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <item.icon className={cn("h-4 w-4", isActive ? "text-primary" : "text-muted-foreground")} />
                  {item.name}
                </div>
              </Link>
            )
          })}
        </div>
        <div className="p-4 border-t">
          <Button variant="ghost" className="w-full justify-start text-muted-foreground hover:text-foreground" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </div>

      {/* ── Mobile bottom nav ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-20 bg-card border-t flex items-stretch h-16 safe-bottom">
        {navItems.map((item) => {
          const isActive = location === item.href
          return (
            <Link key={item.href} href={item.href} className="flex-1">
              <div className={cn(
                "flex flex-col items-center justify-center h-full gap-1 transition-colors",
                isActive ? "text-primary" : "text-muted-foreground"
              )}>
                <item.icon className="h-5 w-5" />
                <span className="text-[10px] font-medium leading-none">{item.name}</span>
              </div>
            </Link>
          )
        })}
        <button
          onClick={handleLogout}
          className="flex-1 flex flex-col items-center justify-center gap-1 text-muted-foreground"
        >
          <LogOut className="h-5 w-5" />
          <span className="text-[10px] font-medium leading-none">Logout</span>
        </button>
      </nav>
    </>
  )
}
