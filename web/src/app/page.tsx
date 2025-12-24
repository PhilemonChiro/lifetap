import { redirect } from "next/navigation";
import { getUser } from "@/actions/auth";
import { getRoleBasePath } from "@/config/navigation";
import Link from "next/link";

export default async function Home() {
  const user = await getUser();

  // Redirect authenticated users to their dashboard
  if (user) {
    redirect(getRoleBasePath(user.role));
  }

  // Landing page for unauthenticated users
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-red-50 to-white px-4">
      <div className="text-center">
        <div className="mb-6 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-600 text-white text-2xl font-bold">
            LT
          </div>
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">LifeTap</h1>
        <p className="text-xl text-gray-600 mb-8 max-w-md">
          Emergency Medical Response System for Zimbabwe
        </p>
        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-lg bg-red-600 px-8 py-3 text-white font-medium hover:bg-red-700 transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="inline-flex items-center justify-center rounded-lg border border-gray-300 px-8 py-3 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
