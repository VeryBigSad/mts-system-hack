import React from 'react';
import { AVAILABLE_ACTIONS } from '../types';
import { 
  Ticket, 
  ArrowUpDown, 
  Camera, 
  Snowflake,
  Gauge,
  CreditCard
} from 'lucide-react';

interface ActionPanelProps {
  onActionClick: (description: string) => void;
}

const iconMap = {
  'ticket': Ticket,
  'elevator': ArrowUpDown,
  'camera': Camera,
  'snowflake': Snowflake,
  'gauge': Gauge,
  'credit-card': CreditCard
};

export const ActionPanel: React.FC<ActionPanelProps> = ({ onActionClick }) => {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-screen-xl mx-auto p-4">
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {AVAILABLE_ACTIONS.map((action) => {
            const Icon = iconMap[action.icon as keyof typeof iconMap];
            return (
              <button
                key={action.id}
                className="flex flex-col items-center p-3 rounded-lg hover:bg-gray-50 transition-colors"
                onClick={() => onActionClick(action.description)}
              >
                <Icon className="w-6 h-6 text-blue-600 mb-2" />
                <span className="text-sm text-gray-600 text-center">
                  {action.name}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};