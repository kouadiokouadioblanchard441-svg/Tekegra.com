import { useState, useRef } from "react"
import { 
  useListUsers, 
  useApproveUser, 
  useRejectUser, 
  useBanUser, 
  useUnbanUser, 
  useSetPremium,
  getListUsersQueryKey
} from "@/lib/api-client-react/src/generated/api"
import { useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { NativeSelect } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { format } from "date-fns"
import { toast } from "sonner"
import { Loader2, Search, CheckCircle, XCircle, Ban, ShieldCheck, Crown } from "lucide-react"

export default function Users() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [debouncedSearch, setDebouncedSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  
  // Premium Dialog State
  const [premiumUser, setPremiumUser] = useState<{ id: number, name: string } | null>(null)
  const [premiumDays, setPremiumDays] = useState(30)
  const [premiumActive, setPremiumActive] = useState(true)

  // Use a simple ref-based debounce for search
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current)
    searchTimeoutRef.current = setTimeout(() => {
      setDebouncedSearch(e.target.value)
    }, 500)
  }

  const { data: usersData, isLoading } = useListUsers({
    search: debouncedSearch || undefined,
    status: statusFilter !== "all" ? (statusFilter as any) : undefined,
    limit: 100
  })

  const users = usersData?.users || []

  // Mutations
  const approveMutation = useApproveUser()
  const rejectMutation = useRejectUser()
  const banMutation = useBanUser()
  const unbanMutation = useUnbanUser()
  const premiumMutation = useSetPremium()

  const invalidateUsers = () => {
    queryClient.invalidateQueries({ queryKey: getListUsersQueryKey() })
  }

  const handleAction = (action: 'approve' | 'reject' | 'ban' | 'unban', id: number) => {
    const mutations = {
      approve: approveMutation,
      reject: rejectMutation,
      ban: banMutation,
      unban: unbanMutation
    }
    
    mutations[action].mutate(
      { telegramId: id },
      {
        onSuccess: () => {
          toast.success(`User ${action}d successfully`)
          invalidateUsers()
        },
        onError: () => toast.error(`Failed to ${action} user`)
      }
    )
  }

  const handleSetPremium = () => {
    if (!premiumUser) return
    premiumMutation.mutate(
      { 
        telegramId: premiumUser.id, 
        data: { active: premiumActive, days: premiumDays } 
      },
      {
        onSuccess: () => {
          toast.success("Premium status updated")
          setPremiumUser(null)
          invalidateUsers()
        },
        onError: () => toast.error("Failed to update premium status")
      }
    )
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved': return <Badge variant="success">Approved</Badge>
      case 'pending': return <Badge variant="warning">Pending</Badge>
      case 'rejected': return <Badge variant="destructive">Rejected</Badge>
      case 'banned': return <Badge variant="destructive">Banned</Badge>
      default: return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search by ID or username..." 
            className="pl-9"
            value={search}
            onChange={handleSearchChange}
          />
        </div>
        <div className="w-full sm:w-48">
          <NativeSelect 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="banned">Banned</option>
          </NativeSelect>
        </div>
      </div>

      <Card className="shadow-sm border-border/50">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Telegram ID</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Premium</TableHead>
              <TableHead>Signals Today</TableHead>
              <TableHead>Last Active</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-10">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto text-primary" />
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-10 text-muted-foreground">
                  No users found matching your criteria.
                </TableCell>
              </TableRow>
            ) : (
              users.map(user => (
                <TableRow key={user.telegramId}>
                  <TableCell>
                    <div className="font-medium">{user.firstName} {user.lastName}</div>
                    {user.username && <div className="text-xs text-muted-foreground">@{user.username}</div>}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{user.telegramId}</TableCell>
                  <TableCell>{getStatusBadge(user.approvalStatus)}</TableCell>
                  <TableCell>
                    {user.isPremium ? (
                      <Badge variant="default" className="bg-amber-500 hover:bg-amber-600 text-white"><Crown className="h-3 w-3 mr-1" /> Premium</Badge>
                    ) : (
                      <span className="text-muted-foreground text-sm">Free</span>
                    )}
                  </TableCell>
                  <TableCell>{user.freeSignalsUsedToday} used</TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {user.lastActive ? format(new Date(user.lastActive), 'PPp') : 'Never'}
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    {user.approvalStatus === 'pending' && (
                      <>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Approve" onClick={() => handleAction('approve', user.telegramId)}>
                          <CheckCircle className="h-4 w-4 text-emerald-500" />
                        </Button>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Reject" onClick={() => handleAction('reject', user.telegramId)}>
                          <XCircle className="h-4 w-4 text-rose-500" />
                        </Button>
                      </>
                    )}
                    {user.approvalStatus === 'approved' && !user.isBanned && (
                      <>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Manage Premium" onClick={() => setPremiumUser({ id: user.telegramId, name: user.username || user.firstName || String(user.telegramId) })}>
                          <Crown className="h-4 w-4 text-amber-500" />
                        </Button>
                        <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Ban" onClick={() => handleAction('ban', user.telegramId)}>
                          <Ban className="h-4 w-4 text-rose-500" />
                        </Button>
                      </>
                    )}
                    {user.isBanned && (
                      <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Unban" onClick={() => handleAction('unban', user.telegramId)}>
                        <ShieldCheck className="h-4 w-4 text-emerald-500" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Premium Modal */}
      <Dialog open={!!premiumUser} onOpenChange={(open) => !open && setPremiumUser(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Manage Premium Status</DialogTitle>
            <DialogDescription>
              Set premium subscription for {premiumUser?.name}.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex items-center space-x-2">
              <input 
                type="checkbox" 
                id="active" 
                checked={premiumActive} 
                onChange={(e) => setPremiumActive(e.target.checked)}
                className="rounded border-input text-primary focus:ring-primary h-4 w-4"
              />
              <Label htmlFor="active">Is Premium Active?</Label>
            </div>
            {premiumActive && (
              <div className="space-y-2">
                <Label htmlFor="days">Duration (Days)</Label>
                <Input 
                  id="days" 
                  type="number" 
                  min="1" 
                  value={premiumDays} 
                  onChange={(e) => setPremiumDays(Number(e.target.value))}
                />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPremiumUser(null)}>Cancel</Button>
            <Button onClick={handleSetPremium} disabled={premiumMutation.isPending}>
              {premiumMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
