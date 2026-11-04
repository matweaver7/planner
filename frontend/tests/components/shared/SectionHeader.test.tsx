import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SectionHeader } from '../../../src/components/shared/SectionHeader';

describe('SectionHeader', () => {
  it('renders the label', () => {
    render(<SectionHeader label="Study Topic" />);
    expect(screen.getByText('Study Topic')).toBeInTheDocument();
  });
});
