import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, Briefcase, FileText, LogOut, User, ChevronDown } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const location = useLocation();
  const { isAuthenticated, user, quota, logout } = useAuth();

  const isInterviewPath = location.pathname.startsWith("/interview");
  const isResumePath = location.pathname.startsWith("/resume") || location.pathname === "/";

  // Don't show navigation on login/register pages
  if (location.pathname === "/login" || location.pathname === "/register") {
    return null;
  }

  const handleLogout = async () => {
    await logout();
    setIsProfileOpen(false);
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 font-bold text-xl text-blue-600">
            <span>🎯 AI Career Platform</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {isAuthenticated && (
              <>
                {/* Resume Section */}
                <div className="flex items-center space-x-3">
                  <FileText className="w-4 h-4 text-purple-600" />
                  <Link
                    to="/"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                      isResumePath && !isInterviewPath
                        ? "bg-purple-100 text-purple-900"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    Resume Analyzer
                  </Link>
                </div>

                {/* Interview Section */}
                <div className="flex items-center space-x-3">
                  <Briefcase className="w-4 h-4 text-blue-600" />
                  <Link
                    to="/interview"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                      isInterviewPath
                        ? "bg-blue-100 text-blue-900"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    AI Interview
                  </Link>
                </div>

                {/* Quota Badge */}
                {quota && (
                  <div className="flex items-center space-x-2 text-xs bg-gray-50 border border-gray-200 rounded-full px-3 py-1 text-gray-600">
                    <span title="Analyses remaining today">
                      ⚡ <strong className="text-gray-800">{quota.analyses?.remaining ?? 3}</strong>/3 analyses
                    </span>
                    <span className="text-gray-300">•</span>
                    <span title="Interviews remaining today">
                      🎙️ <strong className="text-gray-800">{quota.interviews?.remaining ?? 2}</strong>/2 interviews
                    </span>
                  </div>
                )}
              </>
            )}
          </div>


          {/* Auth Buttons / Profile */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {user?.full_name?.charAt(0).toUpperCase()}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{user?.full_name}</span>
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                </button>

                {/* Profile Dropdown */}
                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200">
                    <div className="px-4 py-3 border-b border-gray-200">
                      <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                    </div>
                    <Link
                      to="/profile"
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setIsProfileOpen(false)}
                    >
                      <User className="w-4 h-4" />
                      <span>Profile</span>
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-700"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {isAuthenticated && (
              <>
                <Link
                  to="/"
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    isResumePath && !isInterviewPath
                      ? "bg-purple-100 text-purple-900"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  Resume Analyzer
                </Link>
                <Link
                  to="/interview"
                  className={`block px-3 py-2 rounded-md text-base font-medium ${
                    isInterviewPath
                      ? "bg-blue-100 text-blue-900"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  AI Interview
                </Link>
                {quota && (
                  <div className="px-3 py-2 text-xs bg-gray-50 rounded-md border border-gray-100 flex items-center justify-between text-gray-600">
                    <span>⚡ Analyses: <strong>{quota.analyses?.remaining ?? 3}</strong>/3</span>
                    <span>🎙️ Interviews: <strong>{quota.interviews?.remaining ?? 2}</strong>/2</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-2 mt-2">
                  <Link
                    to="/profile"
                    className="flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsOpen(false)}
                  >
                    <User className="w-4 h-4" />
                    <span>Profile</span>
                  </Link>

                  <button
                    onClick={() => {
                      handleLogout();
                      setIsOpen(false);
                    }}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </>
            )}
            {!isAuthenticated && (
              <div className="space-y-2 pt-2 border-t border-gray-200">
                <Link
                  to="/login"
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
                  onClick={() => setIsOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="block px-3 py-2 rounded-md text-base font-medium bg-blue-600 text-white hover:bg-blue-700"
                  onClick={() => setIsOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
