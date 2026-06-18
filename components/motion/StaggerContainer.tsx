"use client";

import { type ReactNode } from "react";

interface StaggerContainerProps {
  children: ReactNode;
  className?: string;
}

export default function StaggerContainer({
  children,
  className = "",
}: StaggerContainerProps) {
  return (
    <div className={`stagger-container ${className}`}>
      {children}
    </div>
  );
}
