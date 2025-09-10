import React from 'react';
import {AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {TitleSlide} from './sections/TitleSlide';
import {OverviewSlide} from './sections/OverviewSlide';
import {ArchSlide} from './sections/ArchSlide';
import {ExampleSlide} from './sections/ExampleSlide';

export const VIDEO_WIDTH = 1920;
export const VIDEO_HEIGHT = 1080;
export const VIDEO_FPS = 30;

// Durations per section (in frames)
const TITLE_DUR = 120; // 4s
const OVERVIEW_DUR = 240; // 8s
const ARCH_DUR = 240; // 8s
const EXAMPLES_DUR = 600; // 20s

export const VIDEO_DURATION = TITLE_DUR + OVERVIEW_DUR + ARCH_DUR + EXAMPLES_DUR;

export type ExampleStep = {
  title: string;
  kind: 'sql' | 'select' | 'insert' | 'delete' | 'create' | 'stats' | 'info';
  sql?: string;
  result?: string | any[];
  elapsed_ms?: number;
};

export const MandukyaVideo: React.FC<{examples: {steps: ExampleStep[]}}> = ({examples}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#0b1021', color: '#E6E8F2', fontFamily: 'system-ui, Inter, Segoe UI, Roboto, sans-serif'}}>
      <AbsoluteFill style={{opacity}}>
        <Sequence durationInFrames={TITLE_DUR}>
          <TitleSlide/>
        </Sequence>
        <Sequence from={TITLE_DUR} durationInFrames={OVERVIEW_DUR}>
          <OverviewSlide/>
        </Sequence>
        <Sequence from={TITLE_DUR + OVERVIEW_DUR} durationInFrames={ARCH_DUR}>
          <ArchSlide/>
        </Sequence>
        <Sequence from={TITLE_DUR + OVERVIEW_DUR + ARCH_DUR} durationInFrames={EXAMPLES_DUR}>
          <ExampleSlide steps={examples.steps}/>
        </Sequence>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

