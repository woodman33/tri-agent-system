/**
 * Payment Method Selection Modal
 * Customer chooses: Credit Card (Stripe) or Bitcoin (BTCPay)
 */
import React, { useState, useEffect } from 'react';
import { CreditCard, Bitcoin, Info, ChevronRight, Lock, Zap } from 'lucide-react';

export function PaymentMethodModal({ product, onClose }) {
  const [methods, setMethods] = useState(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [selectedMethod, setSelectedMethod] = useState(null);

  // Fetch available payment methods
  useEffect(() => {
    fetch('/api/payment-methods')
      .then(res => res.json())
      .then(data => {
        setMethods(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load payment methods:', err);
        setLoading(false);
      });
  }, []);

  const handlePurchase = async (method) => {
    if (!email) {
      alert('Please enter your email address');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `/api/create-payment/${product}?payment_method=${method}&email=${encodeURIComponent(email)}`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Payment creation failed');
      }

      // Open checkout URL in new window
      window.open(data.checkout_url, '_blank');

      // Show success message
      alert(`Payment window opened! Complete your ${method === 'stripe' ? 'card' : 'Bitcoin'} payment there.`);

    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingView />;
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6">
          <h2 className="text-2xl font-bold mb-2">Choose Your Payment Method</h2>
          <p className="text-white/90">
            {product === 'pro' ? 'Local AI Studio Pro - $9.99' : 'Tri-Agent System - $39.99'}
          </p>
        </div>

        {/* Email Input */}
        <div className="p-6 border-b">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Email (for license delivery)
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            required
          />
        </div>

        {/* Payment Methods */}
        <div className="p-6 space-y-4">
          {methods?.stripe && (
            <PaymentMethodCard
              method="stripe"
              icon={<CreditCard className="w-8 h-8" />}
              title="Credit or Debit Card"
              provider="Stripe"
              fees={methods.stripe.fees}
              processing={methods.stripe.processing_time}
              description={methods.stripe.description}
              features={[
                'All major cards accepted',
                'Instant activation',
                'Secure payment processing',
                'Widely accepted worldwide'
              ]}
              selected={selectedMethod === 'stripe'}
              onSelect={() => setSelectedMethod('stripe')}
              onPurchase={() => handlePurchase('stripe')}
              disabled={loading || !email}
            />
          )}

          {methods?.btcpay && (
            <PaymentMethodCard
              method="btcpay"
              icon={<Bitcoin className="w-8 h-8" />}
              title="Bitcoin / Lightning Network"
              provider="BTCPay Server (Self-Hosted)"
              fees={methods.btcpay.fees}
              processing={methods.btcpay.processing_time}
              description={methods.btcpay.description}
              features={[
                '100% open source',
                'Privacy-focused',
                'No middleman fees',
                'Lightning: Instant & cheap'
              ]}
              badge="PRIVACY"
              selected={selectedMethod === 'btcpay'}
              onSelect={() => setSelectedMethod('btcpay')}
              onPurchase={() => handlePurchase('btcpay')}
              disabled={loading || !email}
            />
          )}
        </div>

        {/* Info Banner */}
        <div className="p-6 bg-blue-50 border-t">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <strong>Your choice, your privacy.</strong> We offer multiple payment methods
              so you can choose what works best for you. All purchases include lifetime
              updates and a 30-day money-back guarantee.
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 bg-gray-50 rounded-b-2xl flex justify-between items-center">
          <p className="text-sm text-gray-600">
            By <strong>Double Down Studios</strong> • One-time purchase
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

function PaymentMethodCard({
  method,
  icon,
  title,
  provider,
  fees,
  processing,
  description,
  features,
  badge,
  selected,
  onSelect,
  onPurchase,
  disabled
}) {
  return (
    <div
      className={`
        relative border-2 rounded-xl p-6 cursor-pointer transition-all
        ${selected
          ? 'border-purple-600 bg-purple-50 shadow-lg'
          : 'border-gray-200 hover:border-purple-300 hover:shadow-md'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      onClick={disabled ? undefined : onSelect}
    >
      {/* Badge */}
      {badge && (
        <span className="absolute -top-3 right-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xs font-bold px-3 py-1 rounded-full">
          {badge}
        </span>
      )}

      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className={`
          p-3 rounded-lg flex-shrink-0
          ${selected ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-600'}
        `}>
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-800 mb-1">{title}</h3>
          <p className="text-sm text-gray-600 mb-3">{provider}</p>

          {/* Description */}
          <p className="text-sm text-gray-700 mb-4">{description}</p>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-white rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Fees</p>
              <p className="text-sm font-semibold text-gray-800">{fees}</p>
            </div>
            <div className="bg-white rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Processing</p>
              <p className="text-sm font-semibold text-gray-800">{processing}</p>
            </div>
          </div>

          {/* Features */}
          <ul className="space-y-2 mb-4">
            {features.map((feature, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                <div className={`w-1.5 h-1.5 rounded-full ${selected ? 'bg-purple-600' : 'bg-gray-400'}`} />
                {feature}
              </li>
            ))}
          </ul>

          {/* Button */}
          {selected && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPurchase();
              }}
              disabled={disabled}
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-bold flex items-center justify-center gap-2 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {method === 'stripe' ? (
                <>
                  <Lock className="w-5 h-5" />
                  Pay with Card
                  <ChevronRight className="w-5 h-5" />
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Pay with Bitcoin
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function LoadingView() {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4" />
        <p className="text-gray-600">Loading payment methods...</p>
      </div>
    </div>
  );
}

export default PaymentMethodModal;
