// arachatfrontend/src/pages/PricingPage.jsx
import React, { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";
import LogoutButton from "../components/LogoutButton";
import { useNavigate } from "react-router-dom";
import { parseJwt } from "../utils/jwt";

export default function PricingPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const userClaims = parseJwt(token);
  const customerId = userClaims?.customer_id;

  useEffect(() => {
    async function fetchPlans() {
      setLoading(true);
      try {
        const data = await apiFetch("/api/pricing");
        setPlans(data.plans);
      } catch (error) {
        console.error("Error fetching plans:", error);
        alert("Failed to fetch plans");
      } finally {
        setLoading(false);
      }
    }
    fetchPlans();
  }, []);

  const handleSubscribe = async (priceId) => {
    try {
      const res = await apiFetch("/api/pricing/checkout", {
        method: "POST",
        body: { customer_id: customerId, price_id: priceId },
      });
      // Redirect the user to Stripe Checkout.
      window.location.href = res.session_url;
    } catch (error) {
      console.error("Subscription error:", error);
      alert("Subscription failed: " + error.message);
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Pricing Plans</h1>
        <LogoutButton />
      </div>
      {loading ? (
        <p>Loading plans...</p>
      ) : (
        <div>
          {plans.map((plan) => (
            <div key={plan.id} className="pricing-card" style={{ border: "1px solid #ddd", padding: "20px", marginBottom: "20px", borderRadius: "8px" }}>
              <h2>{plan.product.name}</h2>
              <p>
                Price: ${(plan.unit_amount / 100).toFixed(2)} {plan.currency.toUpperCase()} per {plan.interval}
              </p>
              <p>Trial: {plan.trial_period_days || 0} days</p>
              {/* Optionally, add token allotment info based on your mapping */}
              <button className="btn" onClick={() => handleSubscribe(plan.id)}>
                Subscribe
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}