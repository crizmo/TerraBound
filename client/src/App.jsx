import React, { useState } from 'react'
import './App.css'
import MapComponent from '@/components/shared/MapComponent'
import SideBar from '@/components/shared/SideBar'
import EditMode from './components/shared/EditMode'

function App() {
  const [textMode, setTextMode] = useState(false)
  const [features, setFeatures] = useState([])
  const [editDetails, setEditDetails] = useState({ id: null, newText: '' });
  const [selectionHandlers, setSelectionHandlers] = useState(null);
  
  // Create a reference to the fetchSegmentationData function
  const handleSegmentationComplete = async () => {
    const mapComponent = document.querySelector('#map-container');
    if (mapComponent && mapComponent.fetchSegmentationData) {
      await mapComponent.fetchSegmentationData();
    }
  };

  return (
    <>
      <div className='w-full h-full' >

        {/* Main Component */}
        <div id="main-container">
          <MapComponent 
            textMode={textMode} 
            editDetails={editDetails} 
            features={features}
            setFeatures={setFeatures}
            setSelectionHandlers={setSelectionHandlers}
          />
          {/* <EditMode textMode={textMode} setTextMode={setTextMode}/> */}
        </div>

        {/* Sidebar */}
        <SideBar 
          features={features} 
          setEditDetails={setEditDetails}
          onSegmentationComplete={handleSegmentationComplete}
          selectionHandlers={selectionHandlers}
        />
      </div>
    </>
  )
}

export default App
