import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const TitleSlide: React.FC = () => {
  const frame = useCurrentFrame();
  const y = interpolate(frame, [0, 30], [40, 0], {extrapolateRight: 'clamp'});
  const opacity = interpolate(frame, [0, 15, 45], [0, 1, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{textAlign: 'center', transform: `translateY(${y}px)`, opacity}}>
        <div style={{fontSize: 64, fontWeight: 800}}>MandukyaDB</div>
        <div style={{marginTop: 16, fontSize: 28, opacity: 0.9}}>A lightweight SQL database inspired by Mandūkya Upaniṣad</div>
        <div style={{marginTop: 40, fontSize: 20, opacity: 0.8}}>Overview • Architecture • Live Examples</div>
      </div>
    </AbsoluteFill>
  );
};

