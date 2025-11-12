import React from 'react';

interface LabelValuePairProps {
  label: string;
  value: React.ReactNode;
}

export default function MediaInfoPair({ label, value }: LabelValuePairProps) {
  if (value === null || value === undefined) {
    return null;
  }
  return (
    <div className="mb-2">
      <div className=" text-[color:var(--media-view-primary-text-color)] text-lg">
        {label}
      </div>
      <div className="text-[color:var(--media-view-secondary-text-color)] text-sm">
        {value}
      </div>
    </div>
  );
}
