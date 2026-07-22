import React from 'react';
import './Skeleton.css';

interface SkeletonProps {
  className?: string;
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
}

export function Skeleton({ className = '', width, height, borderRadius }: SkeletonProps) {
  const style = { width, height, borderRadius };
  return <div className={`skeleton-base ${className}`} style={style} />;
}
