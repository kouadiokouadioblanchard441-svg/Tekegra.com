import { useGetStats } from "@/lib/api-client-react/src/generated/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, UserCheck, Star, Clock, Ban, Activity, Zap } from "lucide-react"
import { Loader } from "@/components/ui/loader"

export default function Dashboard() {
  const { data: stats, isLoading, isError } = useGetStats()

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader className="h-8 w-8" /></div>
  }

  if (isError || !stats) {
    return <div className="text-destructive p-4 border border-destructive/20 rounded-md bg-destructive/10">Failed to load statistics.</div>
  }

  const statCards = [
    { title: "Total Users", value: stats.totalUsers, icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
    { title: "Active Today", value: stats.activeToday, icon: Activity, color: "text-emerald-500", bg: "bg-emerald-500/10" },
    { title: "Premium Users", value: stats.premiumUsers, icon: Star, color: "text-amber-500", bg: "bg-amber-500/10" },
    { title: "Approved", value: stats.approvedUsers, icon: UserCheck, color: "text-indigo-500", bg: "bg-indigo-500/10" },
    { title: "Pending Approval", value: stats.pendingUsers, icon: Clock, color: "text-orange-500", bg: "bg-orange-500/10" },
    { title: "Banned", value: stats.bannedUsers, icon: Ban, color: "text-rose-500", bg: "bg-rose-500/10" },
    { title: "Signals Generated", value: stats.totalSignals, icon: Zap, color: "text-purple-500", bg: "bg-purple-500/10" },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <Card key={i} className="border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-md ${stat.bg}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value.toLocaleString()}</div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Placeholder for future charts or activity feed */}
        <Card className="col-span-1 shadow-sm">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground py-8 text-center border-2 border-dashed rounded-md">
              Activity timeline will appear here
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
