import { create } from 'zustand'

interface Organization {
  id: string
  name: string
  slug: string
  plan: string
  memberCount: number
  createdAt: string
}

interface OrganizationState {
  currentOrganization: Organization | null
  organizations: Organization[]
  setCurrentOrganization: (org: Organization) => void
  setOrganizations: (orgs: Organization[]) => void
}

export const useOrganizationStore = create<OrganizationState>((set) => ({
  currentOrganization: null,
  organizations: [],

  setCurrentOrganization: (org) => {
    localStorage.setItem('currentOrg', org.slug)
    set({ currentOrganization: org })
  },

  setOrganizations: (orgs) => set({ organizations: orgs }),
}))
