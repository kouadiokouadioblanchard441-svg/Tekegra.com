import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { useGetSettings, useUpdateSettings, getGetSettingsQueryKey } from "@/lib/api-client-react/src/generated/api"
import { useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { toast } from "sonner"
import { Loader2, Save, Image as ImageIcon } from "lucide-react"
import { Loader } from "@/components/ui/loader"

export default function Settings() {
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useGetSettings()
  const updateMutation = useUpdateSettings()
  
  const { register, handleSubmit, reset, formState: { isDirty } } = useForm({
    defaultValues: settings || {}
  })

  // Update form when data loads
  useEffect(() => {
    if (settings) {
      reset(settings)
    }
  }, [settings, reset])

  const onSubmit = (data: any) => {
    // Only send the fields that are allowed to be updated
    const payload = {
      promoCode: data.promoCode,
      affiliateLink: data.affiliateLink,
      freeSignalsPerDay: Number(data.freeSignalsPerDay),
      premiumSignalsPerDay: Number(data.premiumSignalsPerDay),
      channel1Link: data.channel1Link,
      channel1Name: data.channel1Name,
      channel2Link: data.channel2Link,
      channel2Name: data.channel2Name,
    }

    updateMutation.mutate(
      { data: payload },
      {
        onSuccess: (updatedData) => {
          toast.success("Settings updated successfully")
          queryClient.setQueryData(getGetSettingsQueryKey(), updatedData)
          reset(updatedData)
        },
        onError: () => toast.error("Failed to update settings")
      }
    )
  }

  if (isLoading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader className="h-8 w-8" /></div>
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Bot Configuration</h2>
            <p className="text-muted-foreground">Manage core bot links, limits, and behavior.</p>
          </div>
          <Button type="submit" disabled={!isDirty || updateMutation.isPending}>
            {updateMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            Save Changes
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-sm border-border/50">
            <CardHeader>
              <CardTitle className="text-lg">Monetization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="promoCode">1WIN Promo Code</Label>
                <Input id="promoCode" {...register("promoCode")} placeholder="e.g. VIP2024" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="affiliateLink">Affiliate Registration Link</Label>
                <Input id="affiliateLink" {...register("affiliateLink")} placeholder="https://1w..." />
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-border/50">
            <CardHeader>
              <CardTitle className="text-lg">Signal Limits</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="freeSignalsPerDay">Free Signals (Per Day)</Label>
                <Input id="freeSignalsPerDay" type="number" {...register("freeSignalsPerDay")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="premiumSignalsPerDay">Premium Signals (Per Day)</Label>
                <Input id="premiumSignalsPerDay" type="number" {...register("premiumSignalsPerDay")} />
                <p className="text-xs text-muted-foreground">Set high for "unlimited"</p>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-border/50 lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">Required Channels</CardTitle>
              <CardDescription>Channels users must subscribe to for approval</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4 p-4 border rounded-md bg-muted/20">
                <div className="font-medium text-sm">Primary Channel</div>
                <div className="space-y-2">
                  <Label>Channel Name</Label>
                  <Input {...register("channel1Name")} placeholder="Main Signals" />
                </div>
                <div className="space-y-2">
                  <Label>Channel Link</Label>
                  <Input {...register("channel1Link")} placeholder="https://t.me/..." />
                </div>
              </div>
              
              <div className="space-y-4 p-4 border rounded-md bg-muted/20">
                <div className="font-medium text-sm">Secondary Channel</div>
                <div className="space-y-2">
                  <Label>Channel Name</Label>
                  <Input {...register("channel2Name")} placeholder="Backup/Chat" />
                </div>
                <div className="space-y-2">
                  <Label>Channel Link</Label>
                  <Input {...register("channel2Link")} placeholder="https://t.me/..." />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </form>

      {/* Read Only Banners Section */}
      <Card className="shadow-sm border-border/50 bg-slate-50/50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center"><ImageIcon className="mr-2 h-5 w-5 text-muted-foreground" /> Current Banners</CardTitle>
          <CardDescription>Currently active image file_ids used by the bot. To update these, send a new photo to the bot directly via Telegram.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {['menuBanner', 'registerBanner', 'luckyjetBanner', 'minesBanner', 'guideBanner'].map((banner) => (
              <div key={banner} className="space-y-1 p-3 border bg-card rounded-md overflow-hidden">
                <div className="text-xs font-medium text-muted-foreground capitalize">{banner.replace('Banner', ' Banner')}</div>
                <div className="text-sm font-mono truncate bg-muted p-1.5 rounded" title={(settings as any)?.[banner] || 'Not set'}>
                  {(settings as any)?.[banner] || <span className="text-muted-foreground italic">Not set</span>}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
