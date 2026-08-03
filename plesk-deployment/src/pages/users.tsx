import { useState, useRef } from "react"
import { 
  useListUsers, 
  useApproveUser, 
  useRejectUser, 
  useBanUser, 
  useUnbanUser, 
  useSetPremium,
  getListUsersQueryKey
} from "@/lib/api-client-react/generated/api"
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
  
  const [premiumUser, setPremiumUser] = useState<{ id: number, name: string } | null>(null)
  const [premiumDays, setPremiumDays] = useState(30)
  const [premiumActive, setPremiumActive] = useState(true)

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

  const approveMutation = useApproveUser()
  const rejectMutation = useRejectUser()
  const banMutation = useBanUser()
  const unbanMutation = useUnbanUser()
  const premiumMutation = useSetPremium()

  const invalidateUsers = () => {
    queryClient.invalidateQueries({ queryKey: getListUsersQueryKey() })
  }

  const handleAction = (action: 'approve' | 'reject' | 'ban' | 'unban', id: number) => {
    const mutations = { approve: approveMutation, reject: rejectMutation, ban: banMutation, unban: unbanMutation }
    mutations[action].mutate(
      { telegramId: id },
      {
        onSuccess: () => { toast.success(`User ${action}d successfully`); invalidateUsers() },
        onError: () => toast.error(`Failed to ${action} user`)
      }
    )
  }

  const handleSetPremium = () => {
    if (!premiumUser) return
    premiumMutation.mutate(
      { telegramId: premiumUser.id, data: { active: premiumActive, days: premiumDays } },
      {
        onSuccess: () => { toast.success("Premium status updated"); setPremiumUser(null); invalidateUsers() },
        onError: () => toast.error("Failed to update premium status")
      }
    )
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved': return <Badge variant="success">Approuvé</Badge>
      case 'pending': return <Badge variant="warning">En attente</Badge>
      case 'rejected': return <Badge variant="destructive">Rejeté</Badge>
      case 'banned': return <Badge variant="destructive">Banni</Badge>
      default: return <Badge variant="outline">{status}</Badge>
    }
  }

  const ActionButtons = ({ user }: { user: any }) => (
    <div className="flex items-center gap-2">
      {user.approvalStatus === 'pending' && (
        <>
          <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Approuver" onClick={() => handleAction('approve', user.telegramId)}>
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          </Button>
          <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Rejeter" onClick={() => handleAction('reject', user.telegramId)}>
            <XCircle className="h-4 w-4 text-rose-500" />
          </Button>
        </>
      )}
      {user.approvalStatus === 'approved' && !user.isBanned && (
        <>
          <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Premium" onClick={() => setPremiumUser({ id: user.telegramId, name: user.username || user.firstName || String(user.telegramId) })}>
            <Crown className="h-4 w-4 text-amber-500" />
          </Button>
          <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Bannir" onClick={() => handleAction('ban', user.telegramId)}>
            <Ban className="h-4 w-4 text-rose-500" />
          </Button>
        </>
      )}
      {user.isBanned && (
        <Button size="sm" variant="outline" className="h-8 w-8 p-0" title="Débannir" onClick={() => handleAction('unban', user.telegramId)}>
          <ShieldCheck className="h-4 w-4 text-emerald-500" />
        </Button>
      )}
    </div>
  )

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      {/* Filters */}
      <div className="flex flex-col gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Rechercher par ID ou username..." 
            className="pl-9 w-full"
            value={search}
            onChange={handleSearchChange}
          />
        </div>
        <NativeSelect 
          value={statusFilter} 
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full"
        >
          <option value="all">Tous les statuts</option>
          <option value="pending">En attente</option>
          <option value="approved">Approuvés</option>
          <option value="rejected">Rejetés</option>
          <option value="banned">Bannis</option>
        </NativeSelect>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex justify-center py-10">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
        </div>
      )}

      {/* Empty */}
      {!isLoading && users.length === 0 && (
        <div className="text-center py-10 text-muted-foreground text-sm">
          Aucun utilisateur trouvé.
        </div>
      )}

      {/* ── Mobile: card list ── */}
      {!isLoading && users.length > 0 && (
        <div className="md:hidden space-y-3">
          {users.map(user => (
            <Card key={user.telegramId} className="shadow-sm border-border/50">
              <CardContent className="p-4 space-y-3">
                {/* Name + premium */}
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="font-medium truncate">
                      {user.firstName} {user.lastName}
                    </div>
                    {user.username && (
                      <div className="text-xs text-muted-foreground">@{user.username}</div>
                    )}
                    <div className="text-xs text-muted-foreground font-mono mt-0.5">
                      {user.telegramId}
                    </div>
                  </div>
                  <div className="shrink-0">
                    {user.isPremium ? (
                      <Badge variant="default" className="bg-amber-500 hover:bg-amber-600 text-white">
                        <Crown className="h-3 w-3 mr-1" /> Premium
                      </Badge>
                    ) : (
                      <Badge variant="outline">Free</Badge>
                    )}
                  </div>
                </div>

                {/* Status + signals */}
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  {getStatusBadge(user.approvalStatus)}
                  <span>· {user.freeSignalsUsedToday} signaux aujourd'hui</span>
                </div>

                {/* Last active */}
                {user.lastActive && (
                  <div className="text-xs text-muted-foreground">
                    Actif : {format(new Date(user.lastActive), 'dd/MM/yy HH:mm')}
                  </div>
                )}

                {/* Actions */}
                <div className="pt-1 border-t">
                  <ActionButtons user={user} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* ── Desktop: table ── */}
      {!isLoading && users.length > 0 && (
        <Card className="hidden md:block shadow-sm border-border/50">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Telegram ID</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead>Premium</TableHead>
                <TableHead>Signaux</TableHead>
                <TableHead>Dernière activité</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map(user => (
                <TableRow key={user.telegramId}>
                  <TableCell>
                    <div className="font-medium">{user.firstName} {user.lastName}</div>
                    {user.username && <div className="text-xs text-muted-foreground">@{user.username}</div>}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{user.telegramId}</TableCell>
                  <TableCell>{getStatusBadge(user.approvalStatus)}</TableCell>
                  <TableCell>
                    {user.isPremium ? (
                      <Badge variant="default" className="bg-amber-500 hover:bg-amber-600 text-white">
                        <Crown className="h-3 w-3 mr-1" /> Premium
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground text-sm">Free</span>
                    )}
                  </TableCell>
                  <TableCell>{user.freeSignalsUsedToday} used</TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {user.lastActive ? format(new Date(user.lastActive), 'PPp') : 'Jamais'}
                  </TableCell>
                  <TableCell className="text-right">
                    <ActionButtons user={user} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Premium Modal */}
      <Dialog open={!!premiumUser} onOpenChange={(open) => !open && setPremiumUser(null)}>
        <DialogContent className="mx-4 max-w-sm rounded-xl">
          <DialogHeader>
            <DialogTitle>Gérer le Premium</DialogTitle>
            <DialogDescription>
              Abonnement premium pour {premiumUser?.name}.
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
              <Label htmlFor="active">Premium actif</Label>
            </div>
            {premiumActive && (
              <div className="space-y-2">
                <Label htmlFor="days">Durée (jours)</Label>
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
          <DialogFooter className="flex-row gap-2 justify-end">
            <Button variant="outline" onClick={() => setPremiumUser(null)}>Annuler</Button>
            <Button onClick={handleSetPremium} disabled={premiumMutation.isPending}>
              {premiumMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Enregistrer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
