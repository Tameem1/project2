// arachatfrontend/src/components/SocialLogin.jsx
import React from "react";

export default function SocialLogin() {
  const handleSocialLogin = (provider) => {
    // Simply redirect to the FastAPI OAuth endpoint.
    window.location.href = `http://localhost:8000/auth/oauth/${provider}`;
  };

  return (
    <div>
      <button className="btn" onClick={() => handleSocialLogin("google")}>
        Sign up with Google
      </button>
      <button className="btn" onClick={() => handleSocialLogin("github")}>
        Sign up with GitHub
      </button>
    </div>
  );
}