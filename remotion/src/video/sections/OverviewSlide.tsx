import React from 'react';
import {AbsoluteFill} from 'remotion';

const Bullet: React.FC<{title: string; desc: string}> = ({title, desc}) => (
  <div style={{display: 'flex', gap: 12, marginBottom: 14}}>
    <div style={{width: 8, height: 8, background: '#8FD5FF', borderRadius: 8, marginTop: 10}}/>
    <div>
      <div style={{fontWeight: 700, fontSize: 26}}>{title}</div>
      <div style={{opacity: 0.85, fontSize: 20}}>{desc}</div>
    </div>
  </div>
);

export const OverviewSlide: React.FC = () => {
  return (
    <AbsoluteFill style={{padding: 80}}>
      <div style={{fontSize: 42, fontWeight: 800, marginBottom: 24}}>What is MandukyaDB?</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28}}>
        <div>
          <Bullet title="SQL Core" desc="CREATE, INSERT, SELECT, DELETE with a simple parser and execution engine."/>
          <Bullet title="In-Memory + File" desc="Run in-memory for speed or persist to a file path."/>
          <Bullet title="Cache-Aware" desc="Execution engine tracks stats, cache hits/misses, and performance."/>
        </div>
        <div>
          <Bullet title="Friendly CLI" desc="Interactive shell with .tables, .schema, .describe, .stats, and more."/>
          <Bullet title="Python API" desc="Use MandukyaDB() from Python to run SQL programmatically."/>
          <Bullet title="Educational" desc="Clean, readable code illustrating a minimal database architecture."/>
        </div>
      </div>
    </AbsoluteFill>
  );
};

