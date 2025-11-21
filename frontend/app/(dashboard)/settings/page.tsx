import { ToastProvider } from "@/components/ui/toast";
import { SettingsTabs } from "./_components/settings-tabs";

export default function SettingsPage() {
  return (
    <ToastProvider>
      <SettingsTabs />
    </ToastProvider>
  );
}


