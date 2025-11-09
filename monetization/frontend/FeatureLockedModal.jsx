/**
 * Feature Locked Modal
 * Shows when user tries to use premium feature
 */
import React from 'react';
import { Lock, Check, ExternalLink, X } from 'lucide-react';

export function FeatureLockedModal({ feature, onClose }) {
  const openPurchase = (tier) => {
    const urls = {
      pro: 'https://doubledownstudios.gumroad.com/l/local-ai-studio-pro',
      enterprise: 'https://doubledownstudios.gumroad.com/l/tri-agent-system'
    };

    window.open(urls[tier], '_blank');
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/80 hover:text-white"
          >
            <X className="w-6 h-6" />
          </button>

          <div className="flex items-center gap-3 mb-2">
            <Lock className="w-8 h-8" />
            <h2 className="text-2xl font-bold">{feature} is a Premium Feature</h2>
          </div>

          <p className="text-white/90">
            Unlock advanced capabilities with a one-time purchase
          </p>
        </div>

        {/* Feature Preview */}
        <div className="p-6 border-b">
          <div className="aspect-video bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center mb-4">
            <div className="text-center p-8">
              <Lock className="w-16 h-16 mx-auto mb-4 text-purple-600" />
              <h3 className="text-xl font-bold text-gray-800 mb-2">{feature}</h3>
              <p className="text-gray-600">
                Available in Enterprise tier
              </p>
            </div>
          </div>

          <FeatureDescription feature={feature} />
        </div>

        {/* Pricing Tiers */}
        <div className="p-6 grid md:grid-cols-2 gap-4">
          {/* Pro Tier */}
          <PricingCard
            tier="Pro"
            price="$9.99"
            description="Enhanced chat experience"
            features={[
              'All 4 AI models',
              'Enhanced UI themes',
              'Priority model loading',
              'Custom settings'
            ]}
            badge={null}
            onPurchase={() => openPurchase('pro')}
          />

          {/* Enterprise Tier */}
          <PricingCard
            tier="Enterprise"
            price="$39.99"
            description="Pro + Autonomous Agents"
            features={[
              'Everything in Pro',
              '6-Agent autonomous system',
              'Boyle\'s Law auto-scaling',
              'Dual-layer architecture',
              'Priority support'
            ]}
            badge="BEST VALUE"
            highlighted
            onPurchase={() => openPurchase('enterprise')}
          />
        </div>

        {/* Footer */}
        <div className="bg-gray-50 p-6 rounded-b-2xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                By <strong>Double Down Studios</strong>
              </p>
              <p className="text-xs text-gray-500">
                One-time purchase • Lifetime updates • 30-day guarantee
              </p>
            </div>

            <button
              onClick={onClose}
              className="text-gray-600 hover:text-gray-800 px-4 py-2"
            >
              Maybe Later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function PricingCard({ tier, price, description, features, badge, highlighted, onPurchase }) {
  return (
    <div className={`
      border-2 rounded-xl p-6 relative
      ${highlighted ? 'border-purple-600 shadow-lg scale-105' : 'border-gray-200'}
    `}>
      {badge && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-3 py-1 rounded-full">
          {badge}
        </span>
      )}

      <div className="text-center mb-4">
        <h3 className="text-2xl font-bold text-gray-800 mb-1">{tier}</h3>
        <p className="text-3xl font-bold text-purple-600 mb-2">{price}</p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>

      <ul className="space-y-2 mb-6">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onPurchase}
        className={`
          w-full py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all
          ${highlighted
            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg'
            : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
          }
        `}
      >
        Buy {tier}
        <ExternalLink className="w-4 h-4" />
      </button>
    </div>
  );
}

function FeatureDescription({ feature }) {
  const descriptions = {
    'Tri-Agent System': (
      <div>
        <h4 className="font-bold text-gray-800 mb-2">What you get:</h4>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>• <strong>6 autonomous agents</strong> working together as a team</li>
          <li>• <strong>Agent 1 (Coder):</strong> Focused on coding tasks</li>
          <li>• <strong>Agent 2 (Improver):</strong> Suggests improvements & helps</li>
          <li>• <strong>Agent 3 (Doctor):</strong> Fixes bugs & settles disputes</li>
          <li>• <strong>Shadow Layer:</strong> 3 additional monitoring agents</li>
          <li>• <strong>Auto-scaling:</strong> Spawns more teams for complex tasks</li>
        </ul>
      </div>
    ),
    'Advanced Models': (
      <div>
        <p className="text-sm text-gray-600">
          Unlock 2 additional premium models for specialized tasks.
        </p>
      </div>
    )
  };

  return descriptions[feature] || null;
}

export default FeatureLockedModal;
