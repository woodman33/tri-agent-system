/**
 * License Activation Modal
 * User enters license key after purchase
 */
import React, { useState } from 'react';
import { Key, Mail, Loader, CheckCircle, XCircle } from 'lucide-react';

export function LicenseActivationModal({ onSuccess, onClose }) {
  const [licenseKey, setLicenseKey] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleActivate = async () => {
    setError('');
    setLoading(true);

    try {
      // Call backend license manager
      const response = await fetch('/api/license/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          license_key: licenseKey.trim().toUpperCase(),
          email: email.trim()
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Activation failed');
      }

      // Success!
      setSuccess(true);

      // Download addons
      if (data.addons && data.addons.length > 0) {
        await downloadAddons(data.addons);
      }

      // Wait a moment then close
      setTimeout(() => {
        onSuccess(data);
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadAddons = async (addons) => {
    // Trigger addon downloads
    for (const addon of addons) {
      await fetch(`/api/addons/download/${addon}`, { method: 'POST' });
    }
  };

  const formatLicenseKey = (value) => {
    // Format as XXXX-XXXX-XXXX-XXXX
    const cleaned = value.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
    const parts = cleaned.match(/.{1,4}/g) || [];
    return parts.join('-').slice(0, 19); // Max length
  };

  const handleKeyChange = (e) => {
    setLicenseKey(formatLicenseKey(e.target.value));
  };

  if (success) {
    return <SuccessView onClose={onClose} />;
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Key className="w-8 h-8 text-purple-600" />
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Activate Your License
          </h2>
          <p className="text-gray-600 text-sm">
            Enter the license key from your purchase email
          </p>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleActivate(); }} className="space-y-4">
          {/* License Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              License Key
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={licenseKey}
                onChange={handleKeyChange}
                placeholder="XXXX-XXXX-XXXX-XXXX"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono"
                required
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
              <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              disabled={loading || !licenseKey || !email}
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Activating...
                </>
              ) : (
                'Activate'
              )}
            </button>
          </div>
        </form>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500 mb-2">
            Haven't purchased yet?
          </p>
          <a
            href="https://doubledownstudios.gumroad.com/l/tri-agent-system"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            Buy Tri-Agent System →
          </a>
        </div>
      </div>
    </div>
  );
}

function SuccessView({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 text-center">
        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
          <CheckCircle className="w-12 h-12 text-green-600" />
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          License Activated! 🎉
        </h2>

        <p className="text-gray-600 mb-6">
          Your addons are downloading and will be available in a moment.
        </p>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-purple-800">
            <strong>Tri-Agent System</strong> is now active!<br />
            Check the "Agents" tab to get started.
          </p>
        </div>

        <button
          onClick={onClose}
          className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          Get Started
        </button>
      </div>
    </div>
  );
}

export default LicenseActivationModal;
