/**
 * Upgrade Banner - Shows in free tier
 * Promotes Tri-Agent System addon
 */
import React from 'react';
import { ExternalLink, Sparkles, Users } from 'lucide-react';

export function UpgradeBanner({ onClose }) {
  const openPurchasePage = () => {
    const purchaseUrl = 'https://doubledownstudios.gumroad.com/l/tri-agent-system';

    // Try to get machine ID for pre-fill (optional)
    const machineId = getMachineId();
    const fullUrl = machineId
      ? `${purchaseUrl}?machine_id=${machineId}`
      : purchaseUrl;

    // Open in browser
    window.open(fullUrl, '_blank');
  };

  return (
    <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white rounded-lg shadow-lg p-6 mb-6 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-32 h-32 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-48 h-48 bg-white rounded-full translate-x-1/3 translate-y-1/3"></div>
      </div>

      {/* Content */}
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5" />
            <h3 className="text-lg font-bold">Unlock Autonomous Agents</h3>
          </div>

          <p className="text-white/90 mb-4 max-w-2xl">
            <strong>Tri-Agent System:</strong> 6 agents working together with dynamic spawning.
            Automatically scales from simple to complex tasks using Boyle's Law.
          </p>

          <div className="flex flex-wrap gap-4 mb-4">
            <Feature icon={<Users />} text="6-Agent Team" />
            <Feature icon={<Sparkles />} text="Auto-Scaling" />
            <Feature icon={<Users />} text="Dual-Layer" />
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={openPurchasePage}
              className="bg-white text-purple-600 px-6 py-3 rounded-lg font-bold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg flex items-center gap-2"
            >
              Upgrade to Enterprise - $39.99
              <ExternalLink className="w-4 h-4" />
            </button>

            <a
              href="https://github.com/woodman33/tri-agent-system"
              target="_blank"
              rel="noopener noreferrer"
              className="text-white/90 hover:text-white text-sm underline"
            >
              Learn More →
            </a>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-white/70 hover:text-white ml-4"
            aria-label="Close"
          >
            ✕
          </button>
        )}
      </div>

      {/* Trust badge */}
      <div className="mt-4 pt-4 border-t border-white/20">
        <p className="text-sm text-white/70">
          By <strong>Double Down Studios</strong> • One-time purchase • Lifetime updates
        </p>
      </div>
    </div>
  );
}

function Feature({ icon, text }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <div className="w-5 h-5">{icon}</div>
      <span>{text}</span>
    </div>
  );
}

function getMachineId() {
  // Simple browser fingerprint
  // In production, use proper machine ID from backend
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('fingerprint', 2, 2);
    return canvas.toDataURL().slice(-50);
  } catch {
    return null;
  }
}

export default UpgradeBanner;
