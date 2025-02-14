import React from 'react'
import { BiMenuAltRight } from "react-icons/bi";
import SearchSidebar from '@/components/shared/SearchSidebar'
import FeatureCard from '@/components/shared/FeatureCard'

const SideBar = ({ features, setEditDetails, onSegmentationComplete }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  /************************************************************
   * Rendering
   ************************************************************/
  return (
    <div className="sidebar-open" style={{
      position: 'absolute',
      top: 0,
      right: 0,
      width: '400px',
      height: '100vh',
      backgroundColor: 'white',
      padding: '20px',
      overflowY: 'auto',
      boxShadow: '-2px 0 5px rgba(0,0,0,0.1)',
      zIndex: 1000
    }}>
      {features.map(feature => (
        <FeatureCard 
          key={feature._leaflet_id}
          feature={feature}
          setEditDetails={setEditDetails}
          onSegmentationComplete={onSegmentationComplete}
        />
      ))}
    </div>
  )
}

export default SideBar
