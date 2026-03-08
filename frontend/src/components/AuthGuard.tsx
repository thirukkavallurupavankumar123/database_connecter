"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

export default function AuthGuard({ children }: { children: ReactNode }) {
  const [checked, setChecked] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("argo_user_id");
    if (!userId) {
      window.location.href = "/login";
      return;
    }
    setAuthed(true);
    setChecked(true);
  }, []);

  if (!checked || !authed) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400 text-sm">Checking authentication...</p>
      </div>
    );
  }

  return <>{children}</>;
}
