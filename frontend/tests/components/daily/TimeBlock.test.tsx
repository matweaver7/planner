import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TimeBlock } from '../../../src/components/daily/TimeBlock';

describe('TimeBlock', () => {
  it('renders the time label', () => {
    render(<TimeBlock time="09:00" text="" onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByText('09:00')).toBeInTheDocument();
  });

  it('renders an input with the current text', () => {
    render(<TimeBlock time="09:00" text="Team standup" onChange={vi.fn()} onBlur={vi.fn()} />);
    expect(screen.getByDisplayValue('Team standup')).toBeInTheDocument();
  });

  it('calls onChange when input changes', async () => {
    const onChange = vi.fn();
    render(<TimeBlock time="09:00" text="" onChange={onChange} onBlur={vi.fn()} />);
    await userEvent.type(screen.getByRole('textbox'), 'lunch');
    expect(onChange).toHaveBeenCalled();
  });

  it('calls onBlur when focus leaves input', async () => {
    const onBlur = vi.fn();
    render(<TimeBlock time="09:00" text="x" onChange={vi.fn()} onBlur={onBlur} />);
    await userEvent.click(screen.getByRole('textbox'));
    await userEvent.tab();
    expect(onBlur).toHaveBeenCalled();
  });
});
