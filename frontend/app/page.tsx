// frontend/app/page.tsx
import { redirect } from "next/navigation";

export default function Home() {
  // Automatically push users to the dashboard (or login) when they hit the root URL
  redirect("/dashboard");
}