import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { RuledField } from '../../../src/components/shared/RuledField';

describe('RuledField', () => {
  it('renders a textarea', () => {
    render(<RuledField aria-label="Notes" value="" onChange={vi.fn()} />);
    expect(screen.getByRole('textbox', { name: 'Notes' })).toBeInTheDocument();
  });

  it('calls onChange when typed into', async () => {
    const onChange = vi.fn();
    render(<RuledField aria-label="Notes" value="" onChange={onChange} />);
    await userEvent.type(screen.getByRole('textbox'), 'hello');
    expect(onChange).toHaveBeenCalled();
  });

  it('calls onBlur when focus leaves', async () => {
    const onBlur = vi.fn();
    render(<RuledField aria-label="Notes" value="text" onChange={vi.fn()} onBlur={onBlur} />);
    const textarea = screen.getByRole('textbox');
    await userEvent.click(textarea);
    await userEvent.tab();
    expect(onBlur).toHaveBeenCalled();
  });
});
