"use client";

import { useRouter } from "next/navigation";
import { apiService } from "../../../services/api_service";
import { Button, Card } from "../../../components/combined_ui";

export default function SettingsPage() {
  const router = useRouter();

  const handleLogout = () => {
    apiService.logout();
    router.push("/login");
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
      <Card className="p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Account Preferences</h2>
        <p className="text-sm text-gray-500 mb-6">Manage your session and privacy settings here.</p>
        <Button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 text-white">
          Secure Logout
        </Button>
      </Card>
    </div>
  );
}
