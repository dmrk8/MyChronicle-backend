import React from 'react';

interface IconButtonProps {
  icon: React.ReactNode;
  conditionIcon: React.ReactNode;
  label: string;
  buttonSize?: number;
  onClick?: () => void;
  className?: string;
  condition?: boolean;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  conditionIcon,
  label,
  buttonSize = 40,
  onClick,
  className = '',
  condition,
}) => (
  <button
    className={`group flex flex-col items-center text-white px-4 py-2 cursor-pointer ${className}`}
    onClick={onClick}
    type="button"
    style={{ fontSize: buttonSize }}
  >
    <span className="transition-transform group-hover:scale-110 cursor-pointer duration-200">
      {condition ? conditionIcon : icon}
    </span>
    <span className="text-base mt-1 ">
      {label}
    </span>
  </button>
);

export default IconButton;
