import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useEffect, useRef } from "react";
import "../styles/Header.css";

const Header = () => {
  const { pathname } = useLocation();
  const indicatorRef = useRef(null);
  const navRef = useRef(null);

  const navItems = [
    { name: "Home", path: "/" },
    { name: "All News", path: "/news" },
    // { name: "World", path: "/world" },
    // { name: "Tech", path: "/tech" },
    // { name: "Politics", path: "/politics" },
  ];

  // Update sliding indicator position
  useEffect(() => {
    const active = navRef.current?.querySelector(".nav-link.active");
    if (active && indicatorRef.current) {
      const { offsetLeft, offsetWidth } = active;
      indicatorRef.current.style.width = `${offsetWidth}px`;
      indicatorRef.current.style.left = `${offsetLeft}px`;
    }
  }, [pathname]);

  return (
    <header className="clean-black-header">
      <div className="header-container">
        {/* Logo */}
        <Link to="/" className="logo">
          NewsAnchor
        </Link>

        {/* Navigation */}
        <nav className="nav" ref={navRef}>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${pathname === item.path ? "active" : ""}`}
            >
              {item.name}
            </Link>
          ))}
          <div className="nav-indicator" ref={indicatorRef} />
        </nav>
      </div>
    </header>
  );
};

export default Header;